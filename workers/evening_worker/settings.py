TIME_PULL_TASK = (19,59,0)
TIME_WS_CONNECT = (19,59,59)
TIME_WS_SEND = (20,0,0)
SLEEP_WS=0.1
SLEEP_POST=1
TASKS_TIMEOUT=300
WS_SIZE=120

def make_ws_headers(cookie:str)->dict:
    return {
        "App-Version": "2.1.2.p1",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "Upgrade",
        "Cookie": cookie,
        "Host": "wechat.v2.traceint.com",
        "Origin": "https://web.traceint.com",
        "Pragma": "no-cache",
        "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
        "Sec-WebSocket-Key": "3GOVqiw+VDRQcNdjIUPxig==",
        "Sec-WebSocket-Version": "13",
        "Upgrade": "websocket",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; TAS-AL00 Build/HUAWEITAS-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/107.0.5304.141 Mobile Safari/537.36 XWEB/5043 MMWEBSDK/20221109 MMWEBID/6856 MicroMessenger/8.0.31.2281(0x28001F59) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64"
    }

def make_post_headers(cookie:str)->dict:
    return {
        "POST": "https://wechat.v2.traceint.com/index.php/graphql/ HTTP/1.1",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "App-Version": "2.1.2.p1",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Cookie": cookie,
        "Host": "wechat.v2.traceint.com",
        "Origin": "https://web.traceint.com",
        "Referer": "https://web.traceint.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; TAS-AL00 Build/HUAWEITAS-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/107.0.5304.141 Mobile Safari/537.36 XWEB/5043 MMWEBSDK/20221109 MMWEBID/6856 MicroMessenger/8.0.31.2281(0x28001F59) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64"
    }

def make_json_for_lib(lib_id:str)->dict:
    return {"operationName": "libLayout",
                "query": "query libLayout($libId: Int!) {\n userAuth {\n prereserve {\n libLayout(libId: $libId) {\n max_x\n max_y\n seats_booking\n seats_total\n seats_used\n seats {\n key\n name\n seat_status\n status\n type\n x\n y\n }\n }\n }\n }\n}",
                "variables": {"libId": lib_id}
        }

def make_json_for_seat(lib_id:str,seat_key:str)->dict:
    return {
        "operationName": "save",
        "query": "mutation save($key: String!, $libid: Int!, $captchaCode: String, $captcha: String) {\n userAuth {\n prereserve {\n save(key: $key, libId: $libid, captcha: $captcha, captchaCode: $captchaCode)\n }\n }\n}",
        "variables": {"key": seat_key, "libid": lib_id, "captchaCode": "", "captcha": ""}
        }