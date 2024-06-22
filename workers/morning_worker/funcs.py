import io
import base64
import aiohttp
import asyncio
from PIL import Image
from .settings import *
from utils.ocr import Ocr
from utils import func_debug
from settings import mlog as log

class MUser():
    def __init__(
        self,
        id:int, #user_if
        username:str,
        wx_cookie:str,
        ocr:Ocr,
        ses:aiohttp.ClientSession,
        seats:list[dict[str, str]]
    )->None:
        self._headers = {
            "POST": "https://wechat.v2.traceint.com/index.php/graphql/ HTTP/1.1",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "App-Version": "2.1.2.p1",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Cookie": wx_cookie,
            "Host": "wechat.v2.traceint.com",
            "Origin": "https://web.traceint.com",
            "Referer": "https://web.traceint.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090a13) XWEB/9129 Flue"
        }
        # self._ses = aiohttp.ClientSession()
        self._ses = ses
        self._ocr:Ocr = ocr
        self._seats = seats
        self._id = id
        self._username = username

    #验证码------------------------------------------------------------------
    async def v_jpg_save(self, img_b64)->None:
        """保存验证码"""
        img_binary = base64.b64decode(img_b64)
        image = Image.open(io.BytesIO(img_binary))
        image.save('output_image.jpg', 'JPEG')

    @func_debug
    async def code_get(self)->dict[str,str]:
        """请求二维码以及code"""
        url = "https://wechat.v2.traceint.com/index.php/graphql/"
        json = {"operationName": "captcha", "query": "query captcha {\n captcha {\n code\n data\n }\n}"}
        
        async with self._ses.post(url=url, headers=self._headers, json=json) as rep:
            ret = await rep.json()
            if 'error' in ret:
                return ''
            if 'data' not in ret:
                return ''
            v_img_base64 = ret['data']['captcha']['data'].split(",")[1]
            return {'code': ret['data']['captcha']['code'], 'img_64': v_img_base64}

    @func_debug
    async def code_get_v(self)->any:
        """获取并识别验证码\n{'ret':True, 'captchaCode': data['code'], 'captcha': captcha}"""
        for _ in range(2):
            self.debug('in_code_get_v')
            data = await self.code_get()
            
            self.debug('out_code_get')
            captcha = await self._ocr.ocr_v(data['img_64'])
            self.debug('out_code_get_v')
            
            if len(captcha) == 4:
                return {'ret':True, 'captchaCode': data['code'], 'captcha': captcha}
        #两次未能获取长度为4的验证码
        return {'ret':False, 'captchaCode': None, 'captcha': None}

    #请求---------------------------------------------------------------------------------
    @func_debug
    async def get_lib_list(self):
        """获取楼层列表"""
        self.info('in_get_lib_list')
        pyload = {
            "operationName": "list",
            "query": "query list {\n userAuth {\n reserve {\n libs(libType: -1) {\n lib_id\n lib_floor\n is_open\n lib_name\n lib_type\n lib_group_id\n lib_comment\n lib_rt {\n seats_total\n seats_used\n seats_booking\n seats_has\n reserve_ttl\n open_time\n open_time_str\n close_time\n close_time_str\n advance_booking\n }\n }\n libGroups {\n id\n group_name\n }\n reserve {\n isRecordUser\n }\n }\n record {\n libs {\n lib_id\n lib_floor\n is_open\n lib_name\n lib_type\n lib_group_id\n lib_comment\n lib_color_name\n lib_rt {\n seats_total\n seats_used\n seats_booking\n seats_has\n reserve_ttl\n open_time\n open_time_str\n close_time\n close_time_str\n advance_booking\n }\n }\n }\n rule {\n signRule\n }\n }\n}"
            }
        url = 'https://wechat.v2.traceint.com/index.php/graphql/'
        await self._ses.post(url=url, headers=self._headers, json=pyload)

    @func_debug
    async def get_unknow_js(self):
        """位置js可能会校验"""
        self.info('in_get_unknow_js')
        url = 'https://web.traceint.com/web/static/js/pages-reserve-seatMap.d4923a8b.js'
        await self._ses.get(url=url, headers=self._headers)

    @func_debug
    async def get_lib(self, libId:str):
        """获取楼层"""
        json = {"operationName": "libLayout",
                "query": "query libLayout($libId: Int, $libType: Int) {\n userAuth {\n reserve {\n libs(libType: $libType, libId: $libId) {\n lib_id\n is_open\n lib_floor\n lib_name\n lib_type\n lib_layout {\n seats_total\n seats_booking\n seats_used\n max_x\n max_y\n seats {\n x\n y\n key\n type\n name\n seat_status\n status\n }\n }\n }\n }\n }\n}",
                "variables": {"libId": libId}}
        url = 'https://wechat.v2.traceint.com/index.php/graphql/'
        await self._ses.post(url=url, headers=self._headers, json=json)

    async def get_seat(
        self, seatKey: str, libId: int, captchaCode: str = '', captcha: str = ''
    ) -> int:
        """
        请求座位列表
        :return: 后端响应
        """
        json = {"operationName": "reserueSeat",
                "query": "mutation reserueSeat($libId: Int!, $seatKey: String!, $captchaCode: String, $captcha: String!) {\n userAuth {\n reserve {\n reserueSeat(\n libId: $libId\n seatKey: $seatKey\n captchaCode: $captchaCode\n captcha: $captcha\n )\n }\n }\n}",
                "variables": {"seatKey": seatKey, "libId": libId, "captchaCode": captchaCode, "captcha": captcha}}
        url = 'https://wechat.v2.traceint.com/index.php/graphql/'
        async with self._ses.post(url=url, headers=self._headers, json=json) as rep:
            rep = await rep.text()
            return rep

    async def task_chain(self, libId: int, seatKey: str)->bool:
        """
        单一座位请求操作集合

        :param ses: aiohttp.ClientSession
        :param ocr: ddddocr.DdddOcr
        :param libId: 楼层id
        :param seatKey: 座位key注意不加"." !!!
        :return: False失败 True成功
        """
        self.debug('in_task_chain')
        post_data = {'libId': libId, 'seatKey': seatKey, 'captchaCode': '', 'captcha': ''}
        
        for _ in range(2):
            ret = await self.code_get_v()
            #返回False说明超过多次未能获取正确长度的验证码
            if not ret['ret']:
                continue
            else:
                post_data['captchaCode'] = ret['captchaCode']
                post_data['captcha'] = ret['captcha']
                self.debug(post_data) 
                await self.get_lib(libId=libId)
                rep = await self.get_seat(**post_data)
                self.debug(rep)
                if 'errors' not in rep:
                    self.info(f'{self._username}-选座成功')
                    return True
                elif r'\u8bf7\u8f93\u5165\u9a8c\u8bc1\u7801' in rep:
                    #验证码错误无需处理
                    self.warning("验证码错误")
                    await asyncio.sleep(POST_SLEEP)
                elif  r'\u60a8\u5df2\u7ecf\u9884\u5b9a\u4e86\u5ea7\u4f4d' in rep:
                    self.info(f'{self._username}-用户已预约过座位')
                    return True
                elif r'\u8be5\u5ea7\u4f4d\u5df2\u7ecf\u88ab\u4eba\u9884\u5b9a\u4e86' in rep:
                    self.info(f'{self._username}-该座位已被抢')
                    await asyncio.sleep(POST_SLEEP)
                    return False
                elif r'\u573a\u9986\u5c1a\u672a\u5f00\u653e\uff0c\u65e0\u6cd5\u64cd\u4f5c' in rep:
                    self.info(f'{self._username}-场馆未开放')
                    await asyncio.sleep(POST_SLEEP)
                    return False
                else:
                    #未捕获可能是验证码错误
                    await asyncio.sleep(POST_SLEEP) 
        
        #单一座位两次请求均未能返回成功       
        return False

    async def tasks_group(self) :
        """
        多座位顺序请求

        :param cookie: cookie
        :param seat_list: 座位列表
        :param ocr: Ocr
        :return: {"id":self._id, "result": False | True}
        """
        #模拟用户行文
        self.debug('in_task_group')
        await self.get_lib_list()
        await self.get_unknow_js()
        for seat in self._seats:
            if seat != None:
                try:
                    ret = await self.task_chain(libId=seat['LibId'],seatKey=seat['Key'])
                except Exception as e:
                    self.warning(f"座位请求出错：{e}")
                if ret:
                    return {"id":self._id, "result": True}
        # await self._ses.close()
        #全部失败
        return {"id":self._id, "result": False}
        
    #测试工具---------------------------------------------------------------------------------------------------
    async def get_user_info(self)->str:
        """打印主页数据, 返回stoken"""
        payload = {"operationName": "index",
                "query": "query index($pos: String!, $param: [hash]) {\n userAuth {\n oftenseat {\n list {\n id\n info\n lib_id\n seat_key\n status\n }\n }\n message {\n new(from: \"system\") {\n has\n from_user\n title\n num\n }\n indexMsg {\n message_id\n title\n content\n isread\n isused\n from_user\n create_time\n }\n }\n reserve {\n reserve {\n token\n status\n user_id\n user_nick\n sch_name\n lib_id\n lib_name\n lib_floor\n seat_key\n seat_name\n date\n exp_date\n exp_date_str\n validate_date\n hold_date\n diff\n diff_str\n mark_source\n isRecordUser\n isChooseSeat\n isRecord\n mistakeNum\n openTime\n threshold\n daynum\n mistakeNum\n closeTime\n timerange\n forbidQrValid\n renewTimeNext\n forbidRenewTime\n forbidWechatCancle\n }\n getSToken\n }\n currentUser {\n user_id\n user_nick\n user_mobile\n user_sex\n user_sch_id\n user_sch\n user_last_login\n user_avatar(size: MIDDLE)\n user_adate\n user_student_no\n user_student_name\n area_name\n user_deny {\n deny_deadline\n }\n sch {\n sch_id\n sch_name\n activityUrl\n isShowCommon\n isBusy\n }\n }\n }\n ad(pos: $pos, param: $param) {\n name\n pic\n url\n }\n}",
                "variables": {"pos": "App-首页"}}
        url = 'https://wechat.v2.traceint.com/index.php/graphql/'
        async with self._ses.post(json=payload, url=url, headers=self._headers) as rep:
            data = await rep.json()
            self.debug(f"主页数据: {data}")
            return data['data']['userAuth']['reserve']['getSToken']

    async def cancel_seat(self, stoken)->None:
        """取消预定座位"""
        stoken = await self.get_user_info()
        payload = {"operationName": "reserveCancle",
                "query": "mutation reserveCancle($sToken: String!) {\n userAuth {\n reserve {\n reserveCancle(sToken: $sToken) {\n timerange\n img\n hours\n mins\n per\n }\n }\n }\n}",
                "variables": {"sToken": stoken}}
        url = 'https://wechat.v2.traceint.com/index.php/graphql/'
        await self.ses.post(headers=self._headers, url=url, json=payload)
    
    def debug(self, info:str)->None:
        log.debug(f'{self._username} {info}')

    def info(self, info:str)->None:
        log.info(f'{self._username} {info}')

    def warning(self, info:str)->None:
        log.warning(f'{self._username} {info}')

