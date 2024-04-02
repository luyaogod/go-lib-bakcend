import urllib.request
import urllib.parse
import http.cookiejar
import asyncio

async def get_code(url):
    query = urllib.parse.urlparse(url).query
    codes = urllib.parse.parse_qs(query).get('code')
    if codes:
        return codes.pop()
    else:
        raise ValueError("Code not found in URL")

async def cookie_string_get_parsing(code):
    cookiejar = http.cookiejar.MozillaCookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookiejar))
    opener.open(
        "http://wechat.v2.traceint.com/index.php/urlNew/auth.html?" + urllib.parse.urlencode({
            "r": "https://web.traceint.com/web/index.html",
            "code": code,
            "state": 1
        })
    )
    cookie_items = []
    for cookie in cookiejar:
        cookie_items.append(f"{cookie.name}={cookie.value}")
    cookie_string = '; '.join(cookie_items)
    return cookie_string

async def get_wx_cookie(url):
    code = await get_code(url)
    cookie_string = await cookie_string_get_parsing(code)
    return cookie_string

async def test():
    url = "http://wechat.v2.traceint.com/index.php/graphql/?code=0817KsGa1nVj5H0qC8Ja1jMotd27KsGG&state=1"
    data =  await get_wx_cookie(url)
    print(data)

if __name__ == '__main__':
    asyncio.run(test())

# import asyncio
# import aiohttp
# import urllib.parse
# from yarl import URL
#
# async def get_code(url):
#     query = urllib.parse.urlparse(url).query
#     codes = urllib.parse.parse_qs(query).get('code')
#     if codes:
#         return codes.pop()
#     else:
#         raise ValueError("Code not found in URL")
#
# async def get(url):
#     code = await get_code(url)
#     async with aiohttp.ClientSession(cookies=aiohttp.CookieJar(unsafe=True)) as session:
#         # 使用 aiohttp 的 URL 和查询参数构造方法
#         auth_url = (
#             f"http://wechat.v2.traceint.com/index.php/urlNew/auth.html?"
#             f"r=https%3A%2F%2Fweb.traceint.com%2Fweb%2Findex.html&"
#             f"code={code}&state=1"
#         )
#         async with session.get(auth_url) :
#             cookies = session.cookie_jar.filter_cookies(URL(url)).output()
#             cookie_strings = cookies.split("Set-Cookie: ")
#             clean_cookies = ""
#             for cookie in cookie_strings:
#                 if cookie != "":
#                     clean_cookie = cookie.replace("\015\012","")
#                     clean_cookies = clean_cookies + clean_cookie + "; "
#     await session.close()
#     return clean_cookies
#
#
# async def get_wx_cookie():
#     url = "http://wechat.v2.traceint.com/index.php/graphql/?operationName=i&code=0410zE100YraSR1Dvo300jh0sW10zE1u&state=1"
#     data =  await get(url)
#     print(data)
#
# if __name__ == '__main__':
#     asyncio.run(get_wx_cookie())