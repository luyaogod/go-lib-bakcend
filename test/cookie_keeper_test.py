from aiohttp import CookieJar,ClientSession,hdrs
from datetime import datetime
import http.cookies
import asyncio


FIRST_SLEEP = 60
SECOND_SLEEP = 3600+3000

async def keeper(wx_cookie):


    jar = CookieJar(unsafe=True)
    try:
        cookie = http.cookies.SimpleCookie()
        cookie.load(wx_cookie)
        for key, morsel in cookie.items():
            jar.update_cookies({key: morsel})
    except Exception as e:
        print("[error-keeper]:cookie处理失败:",e)
        return

    data = {
        "operationName": "getUserCancleConfig",
        "query": "query getUserCancleConfig {\n userAuth {\n user {\n holdValidate: getSchConfig(fields: \"hold_validate\", extra: true)\n }\n }\n}",
        "variables": {
        }}

    async with ClientSession(cookie_jar=jar) as session:
        update_cookie = False
        sleep_time = 60
        while True:

            async with session.post("http://wechat.v2.traceint.com/index.php/graphql/", data=data) as rep:

                rep_text = await rep.text()

                if "errors" in rep_text:
                    print("[cookie失效]",datetime.now())
                    break

                print("[cookie有效]:", datetime.now())

                rep_header = rep.headers.getall(hdrs.SET_COOKIE) #检查响应头

                if update_cookie == True:
                    req_header = rep.request_info.headers.get('Cookie')
                    print('[cookie更新]:',f'{datetime.now()}',req_header)

                is_find_Authorization = False
                for i in rep_header:
                    if "Authorization=" in i:
                        print("[find]:Set-Cookie:Authorization")
                        is_find_Authorization = True

                if  is_find_Authorization == True:
                    update_cookie = True
                    sleep_time = 3600 + 3000
                    continue
            print('[sleep]:',sleep_time)
            print("-------------------------------------------")
            await asyncio.sleep(sleep_time)
            update_cookie = False
            sleep_time = 60



if __name__ == "__main__":
    cookie_string = "Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjExMjY5MTI5LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNzEzMTU5NDkwfQ.PURcd0OgSrMieK2qZuvH9Te9-_FPBWWb_26wbeQhXxIjClZfZl9VmVZdW21Sr_Lc-_MO7HzW2msvze4GPf-wkSeVTy-O3Meujs7rjoOeZKqnezh7IhcvWPNtRdbMhvHHwbjWc11i9mOPlT_hOvziweF3LBw3AUAbExsp5p8mXHFrAgwM9PzknsSi4-_K4Pf8NwVzA3Bf-087CiSdY599B7Za-fkFuzWoRJIrgd6ALsptYZEU99KMlDPjIuOR5EkNaOLsJg5p9DqDAsjaV5zSrT3eU5gdv3Lw48SEMhjtT5ZtEG0SANxfe-ez7Kap9kP5YFOjgBNdWgeVGvjGvymq5A; SERVERID=82967fec9605fac9a28c437e2a3ef1a4|1713152290|1713152290;"
    asyncio.run(keeper(cookie_string))