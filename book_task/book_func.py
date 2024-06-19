import aiohttp
from models import User,Task,Task_Ret
from typing import Optional,List,Tuple
from utils.clock import clock
from .book_utils import make_ws_headers,make_post_headers,make_json_for_lib,make_json_for_seat
import asyncio
from datetime import datetime
from settings import mlog as log


class UserQ:
    def __init__(self,user_id:int):
        self.user_id = user_id

    async def get_user_info(self)->Optional[User]:
        """
        查询用户信息
        :return:
        """
        user = await User.get_or_none(id=self.user_id)
        return user

    async def get_user_seats(self)->Optional[List]:
        """
        获取用户座位表
        :return:
        """
        user = await User.get_or_none(id=self.user_id)
        data = await user.seats.all().prefetch_related('lib')
        if not len(data) < 1:
            seat_list = []
            for i in data:
                data_dict = {}
                data_dict['lib_id'] = i.lib.lib_id
                data_dict['seat_key'] = i.seat_key
                seat_list.append(data_dict)
            return seat_list
        else:
            return None

    async def reduce_balance(self)->None:
        """
        用户余额-1
        :return:
        """
        user = await User.get_or_none(id=self.user_id)
        user.balance -= 1
        await user.save()

    async def get_user_cookie_obj(self)->Optional[Task]:
        """
        获取用户<cookie-查询对象>
        :return:
        """
        cookie_obj = await Task.get_or_none(user__id=self.user_id)
        return cookie_obj

    async def get_user_cookie(self)->Optional[str]:
        """
        获取用户cookie
        :return: string
        """
        cookie_obj = await Task.get_or_none(user__id=self.user_id)
        if cookie_obj:
            return cookie_obj.wx_cookie
        else:
            return None
    
    async def add_task_ret(self,ret:int)->None:
        """
        创建任务结果，1成功，0失败
        """
        await Task_Ret.create(user_id=self.user_id, time=datetime.now().date(), status=ret)
        return None
        
class Book(UserQ):
    """
    使用Book需要调用init方法
    """
    def __init__(
            self,
            user_id: int,
            ses:aiohttp.ClientSession,
            ws_send_time: Tuple[int] = (20,0,0),
            ws_size = 100,
            ws_sleep = 0.1,
            post_sleep = 1,
            
    )->None:
        super().__init__(user_id)
        self.seats = None
        self.cookie = None
        self.ws_headers = None
        self.post_headers = None
        self.inited = False
        self.ses = ses
        self.ws_send_time = ws_send_time
        self.ws_size = ws_size
        self.post_sleep = post_sleep
        self.ws_sleep = ws_sleep
        self.ret = False

    async def init(self)->bool:
        self.cookie = await self.get_user_cookie()
        self.seats = await self.get_user_seats()
        if self.cookie == None or self.seats == None:
            return False
        self.ws_headers = make_ws_headers(self.cookie)
        self.post_headers = make_post_headers(self.cookie)
        self.inited = True
        return True

    async def do_ws(self)->bool:
        """
        ws排队动作
        :return:
        """
        result = False
        async with self.ses.ws_connect(
                "wss://wechat.v2.traceint.com/ws?ns=prereserve/queue",
                headers=self.ws_headers) as ws:
            await clock(self.ws_send_time) 
            count = 0
            while count < self.ws_size:
                await ws.send_str('{"ns":"prereserve/queue","msg":""}')
                data = await ws.receive()
                if data.type != aiohttp.WSMsgType.TEXT:
                    log.warning(f"ws-Type Error: {data.type}-重新发送")
                    count += 1
                    continue 
                else:
                    if count == 0:
                        log.info(f'ws-排队名次{data.data}')
                    if data.data == r'{"ns":"prereserve\/queue","msg":"\u6392\u961f\u6210\u529f\uff01\u8bf7\u57282\u5206\u949f\u5185\u9009\u62e9\u5ea7\u4f4d\uff0c\u5426\u5219\u9700\u8981\u91cd\u65b0\u6392\u961f\u3002","code":0,"data":0}':
                        log.info('ws-排队成功')
                        result = True
                        break
                    elif data.data == r'{"ns":"prereserve\/queue","msg":1000}':
                        log.warning(f"ws-cookie失效-user-{self.user_id}")
                        break
                    elif data.data == r'{"ns":"prereserve\/queue","msg":"\u4e0d\u5728\u9884\u7ea6\u65f6\u95f4\u5185,\u8bf7\u5728 20:00-23:59 \u6765\u9884\u7ea6","code":0,"data":0}':
                        log.warning(f"ws-不在预约时间-user{self.user_id}")
                        break
                    elif r"\u4f60\u5df2\u7ecf\u6210\u529f\u767b\u8bb0\u4e86\u660e\u5929\u7684" in data.data:
                        log.info('ws-已预约座位')
                        break
                    await asyncio.sleep(self.ws_sleep)
                    count += 1
            if count >= self.ws_size:
                log.warning('ws-排队超时')
            await ws.close()
        return result

    async def do_post(self,user_seat)->bool:
        """
        请求单个座位动作
        :param user_seat:
        :return:
        """
        ret = False
        url = "https://wechat.v2.traceint.com/index.php/graphql/"
        await self.ses.post(url=url,
                            json=make_json_for_lib(lib_id=user_seat['lib_id']),
                            headers=self.post_headers)
        async with self.ses.post(
                url=url,
                json=make_json_for_seat(lib_id=user_seat['lib_id'],seat_key=user_seat['seat_key']),
                headers=self.post_headers
        ) as rep:
            if "error" not in await rep.text():
                ret = True
            else:
                log.warning(f'post-选座失败-user{self.user_id} { await rep.json() }')
        await asyncio.sleep(self.post_sleep)
        return ret

    async def do_posts(self)->bool:
        """
        请求一组座位动作链
        :return:
        """
        is_success = False
        for seat in self.seats:
            ret = await self.do_post(seat)
            if ret == True:
                is_success = True
                break
        return is_success

    async def do_chain(self)->bool:
        """
        完整的抢座动作链
        :return:
        """
        try:
            ws_result = await self.do_ws()
            if not ws_result:
                self.ret = False
                return False
            else:
                poset_ret = await self.do_posts()
                if not poset_ret:
                    self.ret = False
                    return False
                else:
                    return True
                
        except asyncio.CancelledError:
            self.ret = False
            return False
