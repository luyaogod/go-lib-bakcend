import aiohttp
from aiohttp.client import ClientSession
import asyncio
from datetime import datetime

WS_SLEEP = 0.5
POST_SLEEP = 0.9
WS_SIZE = 20
UA = "Mozilla/5.0 (Linux; Android 10; TAS-AL00 Build/HUAWEITAS-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/107.0.5304.141 Mobile Safari/537.36 XWEB/5043 MMWEBSDK/20221109 MMWEBID/6856 MicroMessenger/8.0.31.2281(0x28001F59) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64"
WS_SUCCESS_QUEUE = r'{"ns":"prereserve\/queue","msg":"\u6392\u961f\u6210\u529f\uff01\u8bf7\u57282\u5206\u949f\u5185\u9009\u62e9\u5ea7\u4f4d\uff0c\u5426\u5219\u9700\u8981\u91cd\u65b0\u6392\u961f\u3002","code":0,"data":0}'
WS_SUCCESS_BOOK = r"\u4f60\u5df2\u7ecf\u6210\u529f\u767b\u8bb0\u4e86\u660e\u5929\u7684"
WS_ERROR_FAIL_COOKIE = r'{"ns":"prereserve\/queue","msg":1000}'

async def ws_headers(cookie):
    ws_headers = {
        "App-Version": "2.1.2.p1",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "Upgrade",
        "Cookie": cookie,
        "Host": "wechat.v2.traceint.com",
        "Origin": "https://web.traceint.com",
        "Pragma": "no-cache",
        "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
        "Sec-WebSocket-Key": "3GOVqiw+VDRQcNdjIUPxig==",
        "Sec-WebSocket-Version": "13",
        "Upgrade": "websocket",
        "User-Agent": UA
    }
    return ws_headers

async def post_headers(cookie):
    post_headers ={
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
        "User-Agent": UA
    }
    return post_headers

def json_for_lib_list(lib_id):
    data = {"operationName":"libLayout","query":"query libLayout($libId: Int!) {\n userAuth {\n prereserve {\n libLayout(libId: $libId) {\n max_x\n max_y\n seats_booking\n seats_total\n seats_used\n seats {\n key\n name\n seat_status\n status\n type\n x\n y\n }\n }\n }\n }\n}","variables":{"libId":lib_id}}
    return data

def json_for_book_seat(lib_id,seat_key):
    json = {
        "operationName": "save",
        "query": "mutation save($key: String!, $libid: Int!, $captchaCode: String, $captcha: String) {\n userAuth {\n prereserve {\n save(key: $key, libId: $libid, captcha: $captcha, captchaCode: $captchaCode)\n }\n }\n}",
        "variables": {"key": seat_key, "libid": lib_id, "captchaCode": "", "captcha": ""}
    }
    return json

async def ws(session:ClientSession,cookie,task_id):
    headers =  await ws_headers(cookie)
    result = False
    async with session.ws_connect("wss://wechat.v2.traceint.com/ws?ns=prereserve/queue",headers=headers) as ws:
        count = 0
        while count<WS_SIZE:
            await ws.send_str('{"ns":"prereserve/queue","msg":""}')
            if count == 0:
                print(f"[ws发出-id{task_id}]",datetime.now())
            data =  await ws.receive()
            if data.type == aiohttp.WSMsgType.TEXT:
                print( "[ws]:",data.json())
                if data.data == WS_ERROR_FAIL_COOKIE:
                    print("[ws]:","<wx-cookie失效>")
                    break
                if data.data == WS_SUCCESS_QUEUE:
                    print("[ws]:", "<排队成功>")
                    result = True
                    break
                if WS_SUCCESS_BOOK in data.data :
                    print("[ws]:", "<已预约座位>")
                    break
                await asyncio.sleep(WS_SLEEP)
                count += 1
            else:
                print("[ws]:", "<data-type错误>:",data.type)
                break
        if count >= WS_SIZE:
            print("[ws]:<排队超时>")
        await ws.close()
    return result

async def post(session:ClientSession,json,cookie,need_response:bool):
    headers = await post_headers(cookie)
    url = "https://wechat.v2.traceint.com/index.php/graphql/"
    async with session.post(url=url,headers=headers,json=json) as rep:
        if need_response == True:
            rep_json = await rep.json()
            print("[ws]:", rep_json)
            rep_detail = await rep.text()
            return rep_detail
        else:
            return None

async def book(wx_cookie,seats,task_id,**kwargs):
    async with aiohttp.ClientSession() as session:
        result = False
        ws_result =  await ws(cookie=wx_cookie,session=session,task_id=task_id)
        if ws_result:
            for i in  seats:
                json1 = json_for_lib_list(lib_id=i["lib_id"])
                json2 = json_for_book_seat(lib_id=i["lib_id"],seat_key=i["seat_key"])
                await post(session=session,json=json1,cookie=wx_cookie,need_response=False)
                rep_text =  await post(session=session, json=json2, cookie=wx_cookie,need_response=True)
                if "error" not in rep_text:
                    print("[post]:<选座成功>")
                    result = True
                    break
                await asyncio.sleep(POST_SLEEP)
        await session.close()
        return {"task_id":task_id,"result":result}
