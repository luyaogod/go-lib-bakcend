import asyncio
import base64
import aiohttp
from PIL import Image
import io
from utils.ocr import Ocr
from settings import mlog as log

POST_SLEEP=0.9

import aiohttp
import asyncio

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

    async def code_v(self, img_b64: str)->str | None:
        """二维码识别,并且校验结果长度是否为4"""
        ret = await self._ocr.ocr_v(img_b64)
        if ret != None:
            if len(ret) != 4:
                return None
            return ret

    async def code_get_v(self)->dict[str:str]:
        """获取并识别验证码\nreturn: {'captchaCode': data['code'], 'captcha': ret}"""
        data = await self.code_get()
        ret = await self.code_v(data['img_64'])

        return {'captchaCode': data['code'], 'captcha': ret}

    #请求---------------------------------------------------------------------------------
    async def get_lib_list(self):
        """获取楼层列表"""
        pyload = {
            "operationName": "list",
            "query": "query list {\n userAuth {\n reserve {\n libs(libType: -1) {\n lib_id\n lib_floor\n is_open\n lib_name\n lib_type\n lib_group_id\n lib_comment\n lib_rt {\n seats_total\n seats_used\n seats_booking\n seats_has\n reserve_ttl\n open_time\n open_time_str\n close_time\n close_time_str\n advance_booking\n }\n }\n libGroups {\n id\n group_name\n }\n reserve {\n isRecordUser\n }\n }\n record {\n libs {\n lib_id\n lib_floor\n is_open\n lib_name\n lib_type\n lib_group_id\n lib_comment\n lib_color_name\n lib_rt {\n seats_total\n seats_used\n seats_booking\n seats_has\n reserve_ttl\n open_time\n open_time_str\n close_time\n close_time_str\n advance_booking\n }\n }\n }\n rule {\n signRule\n }\n }\n}"
            }
        url = 'https://wechat.v2.traceint.com/index.php/graphql/'
        await self._ses.post(url=url, headers=self._headers, json=pyload)

    async def get_unknow_js(self):
        """位置js可能会校验"""
        url = 'https://web.traceint.com/web/static/js/pages-reserve-seatMap.d4923a8b.js'
        await self._ses.get(url=url, headers=self._headers)

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
        print('[进入单任务执行]')
        post_data = {'libId': libId, 'seatKey': seatKey, 'captchaCode': '', 'captcha': ''}
        
        count = 0
        while count < 2:
            #模拟用户行文
            await self.get_lib(libId=libId)
            await self.get_seat(**post_data)
            await asyncio.sleep(POST_SLEEP)

            #正式请求验证码接口
            data = await self.code_get_v()
            post_data['captchaCode'] = data['captchaCode']
            post_data['captcha'] = data['captcha']
            log.debug(post_data) 
            await self.get_lib(libId=libId)
            rep = await self.get_seat(**post_data)
            log.debug(rep)
            if 'errors' not in rep:
                log.info(f'{self._username}-选座成功')
                return True
            elif rep == r'{"errors":[{"msg":"\u64cd\u4f5c\u5931\u8d25, \u60a8\u5df2\u7ecf\u9884\u5b9a\u4e86\u5ea7\u4f4d!","code":1}],"data":{"userAuth":{"reserve":{"reserueSeat":null}}}}':
                log.info(f'{self._username}-用户已预约过座位')
                return True
            elif rep == r'{"errors":[{"msg":"\u8be5\u5ea7\u4f4d\u5df2\u7ecf\u88ab\u4eba\u9884\u5b9a\u4e86!(3)","code":1}],"data":{"userAuth":{"reserve":{"reserueSeat":null}}}}':
                log.info(f'{self._username}-该座位已被抢')
                return False
            elif rep == r'{"errors":[{"msg":"\u573a\u9986\u5c1a\u672a\u5f00\u653e\uff0c\u65e0\u6cd5\u64cd\u4f5c!","code":2}],"data":{"userAuth":{"reserve":{"reserueSeat":null}}}}':
                log.info(f'{self._username}-场馆未开放')
                return False
            await asyncio.sleep(POST_SLEEP)
            count += 1
        return False  # 单一错误超过两次，可能由验证码错误导致

    async def tasks_group(self) :
        """
        多座位顺序请求

        :param cookie: cookie
        :param seat_list: 座位列表
        :param ocr: Ocr
        :return: {"id":self._id, "result": False}
        """
        #模拟用户行文
        await self.get_lib_list()
        await self.get_unknow_js()
        result = False
        for seat in self._seats:
            if seat != None:
                try:
                    ret = await self.task_chain(libId=seat['LibId'],seatKey=seat['Key'])
                except Exception as e:
                    log.warning(f"座位请求出错：{e}")
                if ret:
                    result = True
                    break
        #全部失败
        # await self._ses.close()
        return {"id":self._id, "result": result}
        

    #测试工具---------------------------------------------------------------------------------------------------
    async def get_user_info(self)->str:
        """打印主页数据, 返回stoken"""
        payload = {"operationName": "index",
                "query": "query index($pos: String!, $param: [hash]) {\n userAuth {\n oftenseat {\n list {\n id\n info\n lib_id\n seat_key\n status\n }\n }\n message {\n new(from: \"system\") {\n has\n from_user\n title\n num\n }\n indexMsg {\n message_id\n title\n content\n isread\n isused\n from_user\n create_time\n }\n }\n reserve {\n reserve {\n token\n status\n user_id\n user_nick\n sch_name\n lib_id\n lib_name\n lib_floor\n seat_key\n seat_name\n date\n exp_date\n exp_date_str\n validate_date\n hold_date\n diff\n diff_str\n mark_source\n isRecordUser\n isChooseSeat\n isRecord\n mistakeNum\n openTime\n threshold\n daynum\n mistakeNum\n closeTime\n timerange\n forbidQrValid\n renewTimeNext\n forbidRenewTime\n forbidWechatCancle\n }\n getSToken\n }\n currentUser {\n user_id\n user_nick\n user_mobile\n user_sex\n user_sch_id\n user_sch\n user_last_login\n user_avatar(size: MIDDLE)\n user_adate\n user_student_no\n user_student_name\n area_name\n user_deny {\n deny_deadline\n }\n sch {\n sch_id\n sch_name\n activityUrl\n isShowCommon\n isBusy\n }\n }\n }\n ad(pos: $pos, param: $param) {\n name\n pic\n url\n }\n}",
                "variables": {"pos": "App-首页"}}
        url = 'https://wechat.v2.traceint.com/index.php/graphql/'
        async with self._ses.post(json=payload, url=url, headers=self._headers) as rep:
            data = await rep.json()
            log.debug(f"主页数据: {data}")
            return data['data']['userAuth']['reserve']['getSToken']

    async def cancel_seat(self, stoken)->None:
        """取消预定座位"""
        stoken = await self.get_user_info()
        payload = {"operationName": "reserveCancle",
                "query": "mutation reserveCancle($sToken: String!) {\n userAuth {\n reserve {\n reserveCancle(sToken: $sToken) {\n timerange\n img\n hours\n mins\n per\n }\n }\n }\n}",
                "variables": {"sToken": stoken}}
        url = 'https://wechat.v2.traceint.com/index.php/graphql/'
        await self.ses.post(headers=self._headers, url=url, json=payload)

