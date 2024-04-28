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
