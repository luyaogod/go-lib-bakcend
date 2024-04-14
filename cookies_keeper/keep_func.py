from aiohttp import CookieJar,ClientSession,hdrs
from datetime import datetime
import http.cookies
import asyncio

async def req(cookie_string):
    jar = CookieJar(unsafe=True)
    cookie = http.cookies.SimpleCookie()
    cookie.load(cookie_string)
    for key, morsel in cookie.items():
        jar.update_cookies({key: morsel})

    data = {
        "operationName": "getUserCancleConfig",
        "query": "query getUserCancleConfig {\n userAuth {\n user {\n holdValidate: getSchConfig(fields: \"hold_validate\", extra: true)\n }\n }\n}",
        "variables": {
        }}

    async with ClientSession(cookie_jar=jar) as session:
        print("[测试开始]:",datetime.now())
        print("[cookie-jar]:")
        for i in session.cookie_jar:
            print(i)
        print("-------------------------------------------")
        update_cookie = False
        while True:
            async with session.post("http://wechat.v2.traceint.com/index.php/graphql/", data=data) as rep:
                print("[请求完成]:",datetime.now())
                rep_text = await rep.text()

                if "errors" in rep_text:
                    print("[失效了]:")
                    break
                rep_header = rep.headers.getall(hdrs.SET_COOKIE) #检查响应头

                if update_cookie == True:
                    req_header = rep.request_info.headers.get('Cookie')
                    print('[新cookie]:',req_header)

                is_find_Authorization = False
                for i in rep_header:
                    print(i)
                    if "Authorization=" in i:
                        print("[find]:Set-Cookie:Authorization")
                        is_find_Authorization = True

                if  is_find_Authorization == True:
                    update_cookie = True
                    continue

            update_cookie = False
            print("-------------------------------------------")
            await asyncio.sleep(60)

cookie_string = "Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjExMjY5MTI5LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNzEzMDIzMjE4fQ.yXPWsGZUzXsLl20B9qOOr7ydjuXPlOp8v646EENpFKBfg4Ew8tJpRHduWq_aEXfVNCBjDGyk6hSnm1_JMZBoAYdChhJptBBllo9CF3SVYKTZn-Vg2lMwtaTSN7zsX_8sLNXWztZYxBd9L0eCywdfZONMuWvWoKmr8lKywnTAtYsz-Sn9Jwp44UGQxVPK_V4xEnNoZ2xqoLBAEZFEcEvVRjE9lJXxBhzIe5PkHKoXtbdU3p1DHWXs-GIhEJKz_nEaDKVNGmXilN6ORh7yvhqybzd_rWfgtKWJEhY5YwDcYbhvwlWMM0AXhOd-MWKWztj9BmaNa7_lBNe45LMWtTBO-Q; SERVERID=d3936289adfff6c3874a2579058ac651|1712926084|1712926084; SERVERID= d3936289adfff6c3874a2579058ac651|1713022394|1712926084"

asyncio.run(req(cookie_string))