import aiohttp
import uvloop
from tortoise import Tortoise
from settings import orm_conf,mlog
from models import Task
from utils.clock import clock

class Cancel:
    def __init__(self,cookie:str) -> None:
        self.ses = aiohttp.ClientSession()
        self.cooke = cookie
        self.url = 'https://wechat.v2.traceint.com/index.php/graphql/'
        self.headers ={
        "POST": "https://wechat.v2.traceint.com/index.php/graphql/ HTTP/1.1",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "App-Version": "2.1.2.p1",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Cookie": cookie,
        "Host": "wechat.v2.traceint.com",
        "Origin": "https://web.traceint.com",
        "Referer": "https://web.traceint.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090a13) XWEB/9129 Flue"
        }

    async def get_user_info(self)->str:
        """
        返回stoken
        """
        payload = {"operationName": "index",
                "query": "query index($pos: String!, $param: [hash]) {\n userAuth {\n oftenseat {\n list {\n id\n info\n lib_id\n seat_key\n status\n }\n }\n message {\n new(from: \"system\") {\n has\n from_user\n title\n num\n }\n indexMsg {\n message_id\n title\n content\n isread\n isused\n from_user\n create_time\n }\n }\n reserve {\n reserve {\n token\n status\n user_id\n user_nick\n sch_name\n lib_id\n lib_name\n lib_floor\n seat_key\n seat_name\n date\n exp_date\n exp_date_str\n validate_date\n hold_date\n diff\n diff_str\n mark_source\n isRecordUser\n isChooseSeat\n isRecord\n mistakeNum\n openTime\n threshold\n daynum\n mistakeNum\n closeTime\n timerange\n forbidQrValid\n renewTimeNext\n forbidRenewTime\n forbidWechatCancle\n }\n getSToken\n }\n currentUser {\n user_id\n user_nick\n user_mobile\n user_sex\n user_sch_id\n user_sch\n user_last_login\n user_avatar(size: MIDDLE)\n user_adate\n user_student_no\n user_student_name\n area_name\n user_deny {\n deny_deadline\n }\n sch {\n sch_id\n sch_name\n activityUrl\n isShowCommon\n isBusy\n }\n }\n }\n ad(pos: $pos, param: $param) {\n name\n pic\n url\n }\n}",
                "variables": {"pos": "App-首页"}}
        async with self.ses.post(json=payload, url=self.url, headers=self.headers) as rep:
            data = await rep.json()
            return data['data']['userAuth']['reserve']['getSToken']
            

    async def cancel(self,stoken:str):
        payload = {"operationName": "reserveCancle",
                "query": "mutation reserveCancle($sToken: String!) {\n userAuth {\n reserve {\n reserveCancle(sToken: $sToken) {\n timerange\n img\n hours\n mins\n per\n }\n }\n }\n}",
                "variables": {"sToken": stoken}}
        await self.ses.post(headers=self.headers, url=self.url, json=payload)
    
    async def do_link(self)->None:
        stoken = await self.get_user_info()
        await self.cancel(stoken=stoken)
        await self.ses.close()

async def main(host:str)->None:
    
    await Tortoise.init(
        config=orm_conf(host)
    )
    mlog.info("CANCEL启动")
    while True:
        await clock((22,30,0))
        tasks = await Task.all()
        cookies = []
        for task in tasks:
            if task.status == 1 and task.open == True and task.wx_cookie != "" and task.wx_cookie != None:
                cookies.append(task.wx_cookie)
        
        for cookie in cookies:
            await Cancel(cookie=cookie).do_link()
            mlog.info("今日任务结束")


def setup_cancel(host:str)->None:
    uvloop.run(main(host=host))
