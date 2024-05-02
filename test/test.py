# import aiohttp
# import asyncio
# from datetime import datetime,timedelta
#
# async def cookie_test(cookie):
#     url = 'http://wechat.v2.traceint.com/index.php/graphql/'
#     headers = {
#         "Cookie":cookie,
#     }
#     json = {"operationName": "index",
#             "query": "query index {\n userAuth {\n tongJi {\n rank\n allTime\n dayTime\n }\n config: user {\n feedback: getSchConfig(fields: \"adm.feedback\")\n }\n }\n}"}
#     async with aiohttp.ClientSession() as session:
#         async with session.post(url=url,headers=headers,json=json,) as rep:
#             data = await rep.text()
#             print(data)
#             if "errors" not in data:
#                 print("[cookie有效]",data)
#                 return True
#             else:
#                 print("[cookie失效]")
#                 return False
#
# async def sleep_to(target_time):
#     now = datetime.now()
#     if now > target_time:
#         target_time += timedelta(days=1)
#     remaining =  (target_time - now).total_seconds()
#     await asyncio.sleep(remaining)
#
#
# async def keep_test(cookie):
#     while True:
#         ret = await cookie_test(cookie)
#         if not ret:
#             break
#         await asyncio.sleep(60)
#     print("[测试结束]", datetime.now())
#
# async def max_test(cookie):
#     # await asyncio.sleep(3600 + 3000)
#     await cookie_test(cookie)
#     print("[测试结束]", datetime.now())
#
#
# if __name__ == "__main__":
#     cookie = r"Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjExMjY5MTI5LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNzEzMDU3Nzk2fQ.O4n966ZG3ycU4dIpbT962MjaLqaC2G2Dz2DJoj4UGh36aNBhwwK7w9ApZignSBZeQQcBMRPEO2_Evlu9CLncy2EIahb6ruFbj0frhenLD4gbqvQoKEkC4qw30-wa8tYKbStLF-mX0vvADCfjusvKb1FAJAv2Ri7hofvQAWfmDl05Ksl6CSwv9o0Xy-iiBnPZRd1aW4snsHXLm62pcWGW25jlssbDWxJOFQM7o_GeegdAGueKqGx2QhC-qXU4rExrePCkRP4chrJZTJj6JlOEF-wxZ-eh6U8NSiVs1p3FlKaaXnPb7nioL6mxyaMuMhP8ryf2RRYEfxRnJypruXkecg; SERVERID=d3936289adfff6c3874a2579058ac651|1713050596|1712926084; SERVERID=d3936289adfff6c3874a2579058ac651|1713050596|1712926084;Path=/"
#     print("[测试开始]", datetime.now())
#     asyncio.run(max_test(cookie))
import asyncio

import aiohttp
from aiohttp.client import ClientSession

headers = {
    "POST": "https://wechat.v2.traceint.com/index.php/graphql/ HTTP/1.1",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "App-Version": "2.1.2.p1",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Cookie": "FROM_TYPE=weixin; v=5.5; wechatSESS_ID=dab001c0c934ac00ff32ae265f6810a0218110ed2e010321; Hm_lvt_7ecd21a13263a714793f376c18038a87=1714220577,1714298654,1714317837,1714430503; Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjExMjY5MTI5LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNzE0NDM3NzgxfQ.HLqxBLUuM7AgJDOmznKjPFfe7_lkHDL2ruV__WFECWJ3nrMgLaC79WX7WGFcMitFKZhJrkraiHZpI42C4wwtaKWIknjkDQu3Bj8OSdMxnybyaCLgJ_YySs80RXvVbyUcLj1VEBqmVP3F7R-_joxL8-1zYePUiMTeWWWTz9R5_x6Pn3ie87vU7cP6m1eMyVBMlSoYV6W7ZOnh6Yx0UrrP97SEGlpAgexegxrTeAJ8Rn_GXFbkm4FN9bWhwY_KK2578kcTUXEpZ4C32dBXsRDqwhX-fBB51szSPMlrJ4ogaV9db-XqUy51oRf3wxhi-jTToBxHVzFp-P6j97fpyw6idQ; Hm_lpvt_7ecd21a13263a714793f376c18038a87=1714430966; SERVERID=e3fa93b0fb9e2e6d4f53273540d4e924|1714430966|1714430497",
    "Host": "wechat.v2.traceint.com",
    "Origin": "https://web.traceint.com",
    "Referer": "https://web.traceint.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090a13) XWEB/9129 Flue"
}
url = "https://wechat.v2.traceint.com/index.php/graphql/"

# json = {"operationName":"reserueSeat","query":"mutation reserueSeat($libId: Int!, $seatKey: String!, $captchaCode: String, $captcha: String!) {\n userAuth {\n reserve {\n reserueSeat(\n libId: $libId\n seatKey: $seatKey\n captchaCode: $captchaCode\n captcha: $captcha\n )\n }\n }\n}","variables":{"seatKey":"15,16","libId":10072,"captchaCode":"","captcha":""}}
json = {"operationName":"captcha","query":"query captcha {\n captcha {\n code\n data\n }\n}"}

async def test():
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, headers=headers, json=json) as rep:
            rep_detail = await rep.json()
            print(rep_detail)



asyncio.run(test())