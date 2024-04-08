# import aiohttp
# from aiohttp.client import ClientSession
# import asyncio
# from datetime import datetime,timedelta
# from book_task.book_run import sleep_to
#
# WS_SLEEP = 0.5
# POST_SLEEP = 0.9
# WS_SIZE = 120
# UA = "Mozilla/5.0 (Linux; Android 10; TAS-AL00 Build/HUAWEITAS-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/107.0.5304.141 Mobile Safari/537.36 XWEB/5043 MMWEBSDK/20221109 MMWEBID/6856 MicroMessenger/8.0.31.2281(0x28001F59) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64"
# WS_SUCCESS_QUEUE = r'{"ns":"prereserve\/queue","msg":"\u6392\u961f\u6210\u529f\uff01\u8bf7\u57282\u5206\u949f\u5185\u9009\u62e9\u5ea7\u4f4d\uff0c\u5426\u5219\u9700\u8981\u91cd\u65b0\u6392\u961f\u3002","code":0,"data":0}'
# WS_SUCCESS_BOOK = r"\u4f60\u5df2\u7ecf\u6210\u529f\u767b\u8bb0\u4e86\u660e\u5929\u7684"
# WS_ERROR_FAIL_COOKIE = r'{"ns":"prereserve\/queue","msg":1000}'
#
# async def ws_headers(cookie):
#     ws_headers = {
#         "App-Version": "2.1.2.p1",
#         "Accept-Language": "zh-CN,zh;q=0.9",
#         "Cache-Control": "no-cache",
#         "Connection": "Upgrade",
#         "Cookie": cookie,
#         "Host": "wechat.v2.traceint.com",
#         "Origin": "https://web.traceint.com",
#         "Pragma": "no-cache",
#         "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
#         "Sec-WebSocket-Key": "3GOVqiw+VDRQcNdjIUPxig==",
#         "Sec-WebSocket-Version": "13",
#         "Upgrade": "websocket",
#         "User-Agent": UA
#     }
#     return ws_headers
#
# async def post_headers(cookie):
#     post_headers ={
#         "POST": "https://wechat.v2.traceint.com/index.php/graphql/ HTTP/1.1",
#         "Accept": "*/*",
#         "Accept-Encoding": "gzip, deflate, br",
#         "Accept-Language": "zh-CN,zh;q=0.9",
#         "App-Version": "2.1.2.p1",
#         "Connection": "keep-alive",
#         "Content-Type": "application/json",
#         "Cookie": cookie,
#         "Host": "wechat.v2.traceint.com",
#         "Origin": "https://web.traceint.com",
#         "Referer": "https://web.traceint.com/",
#         "Sec-Fetch-Dest": "empty",
#         "Sec-Fetch-Mode": "cors",
#         "Sec-Fetch-Site": "same-site",
#         "User-Agent": UA
#     }



