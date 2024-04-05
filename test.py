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
#     cookie = "Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjExMjY5MTI5LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNzEyMjYzOTEzfQ.x4hlA4j5ZyUPvFatjLVv8KQNhZRYsXkxINTtvJ2RrdYmQSSUL7CCJJ2PsL1xU58ujVYDv-AB5A08gcOaSGjTTkQHYiMnWmsjczPdRGXYvqHJx5iA3QYcb2-5VbZxIVTP93uMM1H3daCl0nCmMU4VT0ZmnrTrgUNcW7bAnJHA1XqP5JUUPB6gE57RWAlyQzxVJ5tA7qUJoduJP4-ImmojZuKedp6DvHbTt1tYQ4-criy-Oi8zNCd0fPpEvbuBNRA_h3_0eioJ9nSSdqFACxRJG7N10rmXWOwxObNbq0JztKM9FBEuznSXfzGg2MFyKHyrlc85d8WLJ2EhAwdhLQ8qIA; SERVERID=d3936289adfff6c3874a2579058ac651|1712256714|1712256714; SERVERID=e3fa93b0fb9e2e6d4f53273540d4e924|1712256713|1712256713"
#     print("[测试开始]", datetime.now())
#     asyncio.run(max_test(cookie))
