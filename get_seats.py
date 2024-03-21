import requests
import websocket
import time

UA = "Mozilla/5.0 (Linux; Android 10; TAS-AL00 Build/HUAWEITAS-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/107.0.5304.141 Mobile Safari/537.36 XWEB/5043 MMWEBSDK/20221109 MMWEBID/6856 MicroMessenger/8.0.31.2281(0x28001F59) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64"

#errors
#请线排队再选座
POST_ERROR_WS_TIME_OVER=r'{"errors":[{"msg":"\u8bf7\u5148\u6392\u961f\u518d\u9009\u5ea7","code":40006}],"data":{"userAuth":{"prereserve":{"save":null}}}}'
#座位已被抢
POST_ERROR_SEATS_GETED=r'{"ns":"prereserve\/queue","msg":"\u4f60\u5df2\u7ecf\u6210\u529f\u767b\u8bb0\u4e86\u660e\u5929\u7684,\u90d1\u4e1c\u6821\u533a-2\u697c\u897f\u9605\u89c8\u533a 105\u53f7 \u5ea7\u4f4d","code":0,"data":0}'
#座位已被预约
POST_ERROR_SEATS_BOOKED=r'{"errors":[{"msg":"\u8be5\u5ea7\u4f4d\u5df2\u7ecf\u88ab\u9884\u7ea6,\u8bf7\u6362\u4e2a\u5ea7\u4f4d\u3002","code":1}],"data":{"userAuth":{"prereserve":{"save":null}}}}'
#场馆已满
POST_ERROR_LIB_IS_FULL=r'{"errors":[{"msg":"\u8be5\u573a\u9986\u4eca\u5929\u7684\u540d\u989d\u5df2\u6ee1,\u6362\u4e2a\u9986\u5ba4\u6216\u8005\u660e\u65e9\u8fdb\u884c\u9009\u5ea7","code":1}],"data":{"userAuth":{"prereserve":{"save":null}}}}'
#无效座位
POST_SEAT_UNDEFINED=r'{"errors":[{"msg":"\u8be5\u5ea7\u4f4d\u4e0d\u5b58\u5728","code":1}],"data":{"userAuth":{"prereserve":{"save":null}}}}'
#选座请求过于频繁
TRY_AGAIN_BUSY=r'{"errors":[{"msg":"\u8bf7\u91cd\u65b0\u5c1d\u8bd5","code":1}],"data":{"userAuth":{"prereserve":{"save":null}}}}'
#微信令牌失效
WS_WX_ERROR_COOKIE_OVER = r'{"ns":"prereserve\/queue","msg":1000}'
#排队成功
WS_SUCCESS_QUEUE = r'{"ns":"prereserve\/queue","msg":"\u6392\u961f\u6210\u529f\uff01\u8bf7\u57282\u5206\u949f\u5185\u9009\u62e9\u5ea7\u4f4d\uff0c\u5426\u5219\u9700\u8981\u91cd\u65b0\u6392\u961f\u3002","code":0,"data":0}'
#预约成功
WS_SUCCESS_BOOK = r"\u4f60\u5df2\u7ecf\u6210\u529f\u767b\u8bb0\u4e86\u660e\u5929\u7684"

#settings
POST_URL = "https://wechat.v2.traceint.com/index.php/graphql/"
SLEEP_WS = 0.5
SLEEP_POST =0.7

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
    while count<200:
        ws.connect("wss://wechat.v2.traceint.com/ws?ns=prereserve/queue", header=headers)
        ws.send('{"ns":"prereserve/queue","msg":""}')
        response = ws.recv()
        # print("- ws:",response)
        if WS_SUCCESS_QUEUE == response:
            ws.close()
            print('- ws:排队成功')
            return 1
        if WS_SUCCESS_BOOK in response:
            ws.close()
            print('- ws:选座成功')
            return 2
        if WS_WX_ERROR_COOKIE_OVER == response:
            print('- ws:无效cookie')
            return -1
        ws.close()
        count += 1
        time.sleep(SLEEP_WS)
    print('- ws:排队超时')
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
    count = 0
    while count<3:
        ws_result =  ws(cookie)
        if ws_result == 1:
            index = 0
            while index < len(data_list):
                global SLEEP_POST
                # print(SLEEP_POST)
                data = data_list[index]
                post_get_lib_list(cookie=cookie, lib_id="10073")
                response = post_book_seat(cookie=cookie, lib_id=data["lib_id"], seat_key=data["seat_key"])
                response_text = response.text
                # print(response_text)
                time.sleep(SLEEP_POST)
                if response_text == POST_ERROR_SEATS_BOOKED:
                    index += 1
                    print('- post:座位已被预约')
                    continue
                if response.text == POST_ERROR_SEATS_GETED:
                    index += 1
                    print('- post:座位已被抢')
                    continue
                if response_text == POST_ERROR_LIB_IS_FULL:
                    index += 1
                    print('- post:此楼已满')
                    continue
                if response_text == POST_SEAT_UNDEFINED:
                    index += 1
                    print('- post:座位不存在')
                    continue
                if response_text == TRY_AGAIN_BUSY:
                    SLEEP_POST += 0.1
                    print('- post:请求过于频繁')
                    continue
                if response_text == POST_ERROR_WS_TIME_OVER :
                    print('- post:排队失效')
                    break
                if "error" in response_text:
                    index += 1
                    print('- post:未捕获错误')

        if ws_result == 2:
            # print('- 选座成功')
            return 0
        if ws_result == -1:
            # print('- cookie失效')
            return -200 #cookie失效ws反馈错误
        count +=1
    print('- 主循环超时程序退出')
    return -100 #循环超时


if __name__ == "__main__":
    # cookie = "FROM_TYPE=weixin; v=5.5; wechatSESS_ID=9b25922c9136061f31111864f771c48da5b525691fb60706; Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjExMjY5MTI5LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNzEwNjg0MDc2fQ.pn9X6Qc-yk_FGkD4bfZHKU3V6fPUjuOsODvkfEhirzXYWiKb9E7-_0lhwYie5cY0YnW9GEyhSTGHLdZD-bwebnx-ftWPsapwR4SD9EtkVpf_YMmHy8d4j__LvQFBF3iIKdRrOJcDA3j47bvVtzjx6-2pRvt9GVT3yBZrAOZqm6_VgvqY4tTWShRgnTuBRsdY79BfgocqD95zYj4Z2JWHrXeWD-PMhcl1ulsx1wiVGOu32FlOlxvYEAzsEYYCzANQU6EPz84GdMXOjHwvGiYurybdAsmXk5uoVUtI0sOCreqF2Q60UtqxiMWiJYqliRH3UhtrsCZSz8-llHKBmjCkmQ; Hm_lvt_7ecd21a13263a714793f376c18038a87=1710417518,1710503922,1710590385,1710676879; Hm_lpvt_7ecd21a13263a714793f376c18038a87=1710677137; SERVERID=e3fa93b0fb9e2e6d4f53273540d4e924|1710677141|1710676870"
    # cookie = "FROM_TYPE=weixin; v=5.5; wechatSESS_ID=fe017891e1fef2d4c5dc73278b201e921ab65f7cdaf0d0f4; Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjExMjY5MTI5LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNzEwODU2MTM2fQ.KQiOR0RIpO2GUOJtHqxk7hkaAymdh1JCZaRsy2XCnryEr8QUgODxQSiS6HXZcS8_FI0S9MxAeeJEHXlXNkDhQgaJxmIsdc08rC5iYpg9p9jkhAyX5jhdfcXB7hl1JE2BQV_8WPETTlbpzu5psslTeZ_TArjLPIOn0j9RCCxcAM7qK0Q0LSVyTtMVnJysnU40_5RaCxcsTtjlz_vgxfwzxcALqm-28NuD1HdIDwy01RP6Nok2FERucUfsv3n935ujdIWHPpkc1qiS1epEiGljNDUV-SNVkS-lZa1DAOk28nnVNG6dvg8p7WdzmLRSopUiRhzI6YPeQCJ38eTChwB2Bg; Hm_lvt_7ecd21a13263a714793f376c18038a87=1710590385,1710676879,1710748544,1710848937; SERVERID=82967fec9605fac9a28c437e2a3ef1a4|1710849010|1710847378; Hm_lpvt_7ecd21a13263a714793f376c18038a87=1710849013"
    # cookie = "FROM_TYPE=weixin; v=5.5; wechatSESS_ID=2e73aecbf0ae1c11215bb5333c2f70a31fdbf73d1e4d1b8e; Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjExMjY5MTI5LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNzEwOTQzNjEyfQ.n-WF7HNNM5rEOhgCfT6jwTzsCcHXFb1PcuT56OR0cpqqHA_vNScJixRe2J5GQR1NZ7TYRE-yQNCLyKoEJ6Sf7_lBU75aOvwLQUUACA1JrMhwehAKYk3BTrVoed82xZZatCdy7cazv97N-wVNiVLw9zsXJmHMTTCqlmf2JeA5DJZyz-JLicmEpM0QkjTnN4XFAP_WGSaRZrYRDEUn7xFsLusbyqXTXNswsFFqwPT2JAF2y2PMVITzMWG2EPd-obwJF3UMab4Ya6N0EGJ_O0-l3lg7LtT9qnXpLYiKFco09mVttyQ9ab7_3WdOalNeLhleBpkXk3DkS3jSn8LEfIMmqQ; Hm_lvt_7ecd21a13263a714793f376c18038a87=1710748544,1710848937,1710863114,1710936424; Hm_lpvt_7ecd21a13263a714793f376c18038a87=1710936484; SERVERID=82967fec9605fac9a28c437e2a3ef1a4|1710936484|1710936407"
    cookie="FROM_TYPE=weixin; v=5.5; Hm_lvt_7ecd21a13263a714793f376c18038a87=1710748544,1710848937,1710863114,1710936424; wechatSESS_ID=72fc2f150209e5da7a17acd4e5f532ccb29273d849c8bfef; Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjExMjY5MTI5LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNzEwOTUxMDM4fQ.f2Qz-aom0xJ3aSlYl-np9cNQAhHCMLP7qUXpocfoQemjiKM_IcRw34ogXufozlW6BGVj6Gp8s0gZv4ArBS7ew1rCyhGMqOsZApUF6gNmZMcmSJLZxefGbbhlYViOlYSUqWDrJZdaMBLaJMggu6R2aiuyZmaqiKCIFXZkl9CgVQH4QixqzulhoQ3gxKHv1th-qJdsR77-IlVt7T7UiRmd27jZno-hVid0CzaInJ0na3HtE138RKi-zDzQwYSmXCyoX0gsG_6DZXVzFqmo8lZHVhpyfgmSTKB20bLQHKEH7DSWUA7zke55Xj3j6Yql_NrO48fTjuwpH7XsFJuK0_wqLw; Hm_lpvt_7ecd21a13263a714793f376c18038a87=1710943850; SERVERID=d3936289adfff6c3874a2579058ac651|1710943910|1710943833"
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
    st = time.time()
    result =  main_loop(cookie,data_list)
    end = time.time()
    print(result,end-st)


