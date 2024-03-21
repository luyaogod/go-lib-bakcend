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
    response = opener.open(
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
    # print("\nCookie string: \n")
    # print(cookie_string)
    return cookie_string

async def test():
    url = "http://wechat.v2.traceint.com/index.php/graphql/?code=0817KsGa1nVj5H0qC8Ja1jMotd27KsGG&state=1"
    data =  await get_wx_cookie(url)
    print(data)

if __name__ == '__main__':
    asyncio.run(test())