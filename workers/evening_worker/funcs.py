import asyncio
import aiohttp
from aiohttp import ClientSession
from utils import clock
from settings import mlog as log
from utils import func_debug
from .settings import *
from .sql import Sql

class EUser():
    def __init__(
        self,
        id:int,
        username:str,
        cookie:str,
        seats:list,
        ses:ClientSession = ClientSession()
    ) -> None:
        self.id = id
        self.username = username
        self.cookie = cookie
        self.seats = seats
        self.ret = False
        self.ses  = ses
        if cookie:
            self.ws_headers = make_ws_headers(cookie)
            self.post_headers = make_post_headers(cookie)
    
    async def do_ws(self)->bool:
        """
        ws排队动作
        :return:
        """
        result = False
        async with self.ses.ws_connect(
                "wss://wechat.v2.traceint.com/ws?ns=prereserve/queue",
                headers=self.ws_headers) as ws:
            await clock(TIME_WS_SEND) 
            for count in range(WS_SIZE):
                await ws.send_str('{"ns":"prereserve/queue","msg":""}')
                data = await ws.receive()
                if data.type == aiohttp.WSMsgType.TEXT:
                    if count == 0:
                        self.INFO(f'ws-名次-{data.json()}')
                if data.data == r'{"ns":"prereserve\/queue","msg":1000}':
                    self.WARNING(f"ws-cookie失效")
                    break
                if data.data == r'{"ns":"prereserve\/queue","msg":"\u6392\u961f\u6210\u529f\uff01\u8bf7\u57282\u5206\u949f\u5185\u9009\u62e9\u5ea7\u4f4d\uff0c\u5426\u5219\u9700\u8981\u91cd\u65b0\u6392\u961f\u3002","code":0,"data":0}':
                    self.INFO('ws-排队成功')
                    result = True
                    break
                if r"\u4f60\u5df2\u7ecf\u6210\u529f\u767b\u8bb0\u4e86\u660e\u5929\u7684" in data.data:
                    self.INFO('ws-已预约座位')
                    break
                await asyncio.sleep(SLEEP_WS)
            
            #WS_SIZE次未能正常返回认定超时
            if count == WS_SIZE-1:
                self.WARNING('ws-排队超时')
            await ws.close()
        return result
    
    async def do_post(self,user_seat)->bool:
        """
        请求单个座位动作
        """
        ret = False
        url = "https://wechat.v2.traceint.com/index.php/graphql/"
        await self.ses.post(url=url,
                            json=make_json_for_lib(lib_id=user_seat['LibId']),
                            headers=self.post_headers)
        async with self.ses.post(
                url=url,
                json=make_json_for_seat(seat_key=user_seat['Key'], lib_id=user_seat['LibId']),
                headers=self.post_headers
        ) as rep:
            if "error" not in await rep.text():
                self.INFO('post-选座成功')
                ret = True
            else:
                self.WARNING(f'post-选座失败 { await rep.json() }')
        await asyncio.sleep(SLEEP_POST)
        return ret
    
    async def do_posts(self)->bool:
        """
        请求一组座位动作链
        """
        for seat in self.seats:
            ret = await self.do_post(seat)
            if ret:
                return True
        return False
    
    @func_debug
    async def do_chain(self, db:Sql)->bool:
        """
        完整的抢座动作链
        :return:
        """
        try:
            ws_ret = await self.do_ws()
            if ws_ret:
                ret = await self.do_posts()
                if ret:
                    # 选座成功扣除余额更新记录
                    await db.reduce_b()
                    await db.update_ret(self.id, 1)
                    return True
                # 失败不扣除余额
                await db.update_ret(self.id, 0)
                return False
        except asyncio.CancelledError:
            await db.update_ret(self.id, 0)
            return False

    #debug
    def INFO(self, detail:str):
        log.info(f"{self.username} {detail}")
    
    def DEBUG(self, detail:str):
        log.debug(f"{self.username} {detail}")

    def WARNING(self, detail:str):
        log.warning(f"{self.username} {detail}")
        

