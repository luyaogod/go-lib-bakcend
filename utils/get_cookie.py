import asyncio
import aiohttp
import urllib.parse
from yarl import URL

async def get_wx_cookie(url)->str:
    try:
        #解析code
        query = urllib.parse.urlparse(url).query
        codes = urllib.parse.parse_qs(query).get('code')
        if codes:
            code = codes.pop()
        else:
            return ""
        #发送请求
        clean_cookies = ""  # return
        async with aiohttp.ClientSession(cookies=aiohttp.CookieJar(unsafe=True)) as session:
            auth_url = (
                f"http://wechat.v2.traceint.com/index.php/urlNew/auth.html?"
                f"r=https%3A%2F%2Fweb.traceint.com%2Fweb%2Findex.html&"
                f"code={code}&state=1"
            )
            async with session.get(auth_url) :
                cookies = session.cookie_jar.filter_cookies(URL(url)).output()
                cookie_strings = cookies.split("Set-Cookie: ")
                for cookie in cookie_strings:
                    if cookie != "":
                        clean_cookie = cookie.replace("\015\012","")
                        clean_cookies += clean_cookie + "; "
        await session.close()
        return clean_cookies
    except Exception as e:
        print('wx_cookie请求错误',e)
        return ""


if __name__ == '__main__':
    async def get():
        url = "http://wechat.v2.traceint.com/index.php/graphql/?operationName=i&code=041dkkFa1jBleH0bOuFa1FQxDq1dkkFl&state=1"
        data = await get_wx_cookie(url)
        print(data)
    asyncio.run(get())