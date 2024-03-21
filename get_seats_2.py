import requests
import websocket
import time
import json

UA = "Mozilla/5.0 (Linux; Android 10; TAS-AL00 Build/HUAWEITAS-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/107.0.5304.141 Mobile Safari/537.36 XWEB/5043 MMWEBSDK/20221109 MMWEBID/6856 MicroMessenger/8.0.31.2281(0x28001F59) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64"

POST_URL = "https://wechat.v2.traceint.com/index.php/graphql/"
SLEEP_WS = 0.5
SLEEP_POST =0.7
WSSIZE=100

WS_SUCCESS_QUEUE = r'{"ns":"prereserve\/queue","msg":"\u6392\u961f\u6210\u529f\uff01\u8bf7\u57282\u5206\u949f\u5185\u9009\u62e9\u5ea7\u4f4d\uff0c\u5426\u5219\u9700\u8981\u91cd\u65b0\u6392\u961f\u3002","code":0,"data":0}'
WS_SUCCESS_BOOK = r"\u4f60\u5df2\u7ecf\u6210\u529f\u767b\u8bb0\u4e86\u660e\u5929\u7684"
def ws_headers(cookie):
    ws_headers = {
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
        "User-Agent": UA
    }
    return ws_headers

def post_headers(cookie):
    post_headers ={
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
        "User-Agent": UA
    }
    return post_headers

def ws(cookie):
    headers = ws_headers(cookie)
    ws = websocket.WebSocket()
    count = 0
    while count<WSSIZE:
        ws.connect("wss://wechat.v2.traceint.com/ws?ns=prereserve/queue", header=headers)
        ws.send('{"ns":"prereserve/queue","msg":""}')
        response = ws.recv()
        print(f"- [ws]:{json.loads(response)}",)
        if WS_SUCCESS_BOOK in response:
            print('- [ws]:<已选过座位>')
            return 2
        if WS_SUCCESS_QUEUE == response:
            ws.close()
            print('- [ws]:<排队成功>')
            return 1
        count += 1
        time.sleep(SLEEP_WS)
    print('- [ws]:<排队超时>')
    return -100

def json_for_lib_list(lib_id):
    data = {"operationName":"libLayout","query":"query libLayout($libId: Int!) {\n userAuth {\n prereserve {\n libLayout(libId: $libId) {\n max_x\n max_y\n seats_booking\n seats_total\n seats_used\n seats {\n key\n name\n seat_status\n status\n type\n x\n y\n }\n }\n }\n }\n}","variables":{"libId":lib_id}}
    return data

def post_get_lib_list(cookie,lib_id):
    json =  json_for_lib_list(lib_id)
    headers = post_headers(cookie)
    response = requests.post(url=POST_URL,headers=headers, json=json)
    return response

def json_for_book_seat(lib_id,seat_key):
    json = {
        "operationName": "save",
        "query": "mutation save($key: String!, $libid: Int!, $captchaCode: String, $captcha: String) {\n userAuth {\n prereserve {\n save(key: $key, libId: $libid, captcha: $captcha, captchaCode: $captchaCode)\n }\n }\n}",
        "variables": {"key": seat_key, "libid": lib_id, "captchaCode": "", "captcha": ""}
    }
    return json

def post_book_seat(cookie,lib_id,seat_key):
    json = json_for_book_seat(lib_id=lib_id,seat_key=seat_key)
    headers = post_headers(cookie)
    response = requests.post(url=POST_URL, headers=headers, json=json)
    return response

def main_loop(cookie,data_list):
    ws_result = ws(cookie)
    if ws_result == 1:
        index = 0
        while index < len(data_list):
            global SLEEP_POST
            data = data_list[index]
            post_get_lib_list(cookie=cookie, lib_id="10073")
            response = post_book_seat(cookie=cookie, lib_id=data["lib_id"], seat_key=data["seat_key"])
            response_text = response.text
            print(f'- [post]:{json.loads(response_text)}')
            time.sleep(SLEEP_POST)
            if "error" in response_text:
                index += 1
                continue
            else:
                print('- [post]<选座成功>')
                return True
    elif ws_result == 2:
        return True
    else:
        return False

cookie = "FROM_TYPE=weixin; v=5.5; Hm_lvt_7ecd21a13263a714793f376c18038a87=1710848937,1710863114,1710936424,1710997070; wechatSESS_ID=e6500ea65c693ba3562673025a2e0386fabc54a7baa98183; Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjExMjY5MTI5LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNzExMDMzMDI0fQ.x6D0Hs4E5AJiB8C5-TYx5KZMowf1oG-0P78a5WsL6u7WKDe5MX6MPqfYnVJ-WYbnrGRdMjwNpbk0hGDWuedccBcq4ltAVSGQy_Dv69uLOR1kHjBo8qWaJ0_LBP2I9fC8c8-u6Nb9HT5RJtBas3hAXr9G78JrW5UdpWxzdCcbZkXqtwJtRrPBau-HVZl30A8DBS338gVnJ4A5u8v_oaKHGNi3dmO4vD44Vy2eDIWneI1UkFQu3ChOfDo2ZhgIewuXgJ_Ztz7UxfRe6YUcRVUQvCDn71nf49yef2nGDVwdgXjsQxCDTyC4Z1ECgUPffJuylIuS11dVQ3NMXQdhjtd19A; SERVERID=e3fa93b0fb9e2e6d4f53273540d4e924|1711025824|1711025820; Hm_lpvt_7ecd21a13263a714793f376c18038a87=1711025836"
# cookie ="FROM_TYPE=weixin; v=5.5; Hm_lvt_7ecd21a13263a714793f376c18038a87=1710848937,1710863114,1710936424,1710997070; wechatSESS_ID=a586d48aa869fc4b5222a1e08452b8b4ea45b3a4f4da15d1; Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjExMjY5MTI5LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNzExMDE0NTU0fQ.k2GIKW7Rm97MRx-nP6P09n8hSIDUpF7rhEuSLOnm8GhRtOl0hiWS2A88NfiAEyU8TchgMDYyTdbKWK_SjCOufSgNL9eabUqU2C_Z0HuScKoOiO6Plq4aIbLE3KPuxHSlC_FqeG10viyhfx5jMqZ7EdLnn0-zQPQ_Ak8-KEIDZW9JuAiWmgP9cbCjJaYhhdtoXCr5oqwBa91HPkmrffxX6MT8DoWJPeCfMn3WVtgceD01fs1e07TjD4bkMX7H9TXvWkI-6r6LgpIjzq7Uvvxck_xj_RhKmsAqJ44N5bixRgA1m1x31_6XO-yz2ZTzdnz-qhXqvYQnDtYTCJST5UPLMQ; SERVERID=d3936289adfff6c3874a2579058ac651|1711007381|1711007087; Hm_lpvt_7ecd21a13263a714793f376c18038a87=1711007381"
data_list = [

    {
        "lib_id": "10071",
        "seat_key": "15,13."
        #满
    },
    {
        "lib_id": "10073",
        "seat_key": "25,14."
        #占
    },
    {
        "lib_id": "10073",
        "seat_key": "27,14."
        #占
    },
    # {
    #     "lib_id": "10073",
    #     "seat_key": "27,14."
    #     # 占
    # },
    {
        "lib_id": "10073",
        "seat_key": "25,13."
        # 空
    },
]

main_loop(cookie=cookie,data_list=data_list)