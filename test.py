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
#     await asyncio.sleep(3600 + 3000)
#     await cookie_test(cookie)
#     print("[测试结束]", datetime.now())
#
#
# if __name__ == "__main__":
#     cookie = "Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjExMjY5MTI5LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNzEyMzM0ODUzfQ.Z58i-XAz39dRPVp4WYk5fCDoOViDDLysnL0v4Ti7stLXBKty3DkDu6GlnJErpq17roQeAM1dw1kj4AgX1hxux3GjDuHFCb4n7TKSDU-m79KFmbrfKPDrX8KwKcHm9DaHwgnKICC9c4_OF_ygpTZa1wCDg-4Ic7Quf3o6tEpZ9wAgaGjedl0DGafcRKgh5P46XFy_zLY8M3HdPDcOI304I4IZISPId0kEruAkhKWQgQlIk7pWSFL5opfQCBQLvkPvGjJ-VM_vL2tM5wXvmLw3QEVez1H5icmU_rOWp5XuXRfXXs368KD6gZUAq3nbRdxqzQ_PX5H76uAPjjdnFy75GQ; SERVERID=d3936289adfff6c3874a2579058ac651|1712327653|1712327653; "
#     print("[测试开始]", datetime.now())
#     asyncio.run(keep_test(cookie))

