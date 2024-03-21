import requests
import json
import time


lib = [10073, 10065, 10071, 10072, 10080, 10081, 10082, 10083, 10084, 10085, 10086, 10087, 10088, 10089, 10090, 10091, 10092, 11019, 11033, 11040, 11300, 11054, 11061, 11068, 11075, 11096, 11117, 11131, 11138, 11082, 11103, 11124, 11748]

def data_get(cookie,lib_id):
    headers = {
        "POST": "https://wechat.v2.traceint.com/index.php/graphql/ HTTP/1.1",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "App-Version": "2.1.2.p1",
        "Connection": "keep-alive",
        "Content-Length": "392",
        "Content-Type": "application/json",
        "Cookie": cookie,
        "Host": "wechat.v2.traceint.com",
        "Origin": "https://web.traceint.com",
        "Referer": "https://web.traceint.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6309092b) XWEB/9079 Flue"
    }
    url = 'https://wechat.v2.traceint.com/index.php/graphql/'
    json = {"operationName": "libLayout",
            "query": "query libLayout($libId: Int, $libType: Int) {\n userAuth {\n reserve {\n libs(libType: $libType, libId: $libId) {\n lib_id\n is_open\n lib_floor\n lib_name\n lib_type\n lib_layout {\n seats_total\n seats_booking\n seats_used\n max_x\n max_y\n seats {\n x\n y\n key\n type\n name\n seat_status\n status\n }\n }\n }\n }\n }\n}",
            "variables": {"libId": lib_id}}
    response = requests.post(headers=headers,url=url,json=json)
    return response.json()

def clean_response(data):
    result_list = []
    clean =  data["data"]["userAuth"]["reserve"]["libs"][0]["lib_layout"]["seats"]
    for i in clean:
        new_i_dict = {}
        if i['name'] != '':
            new_i_dict['name'] = i['name']
            new_i_dict['key'] = i['key']
            result_list.append(new_i_dict)
    return result_list

def data_get_and_store(lib,cookie):
    for i in lib:
        data =  data_get(cookie=cookie,lib_id=i)
        clean_data = clean_response(data)
        with open(f'{i}.json','w',encoding='utf-8') as f:
            json.dump(clean_data,f,ensure_ascii=False)
        f.close()
        time.sleep(1)


cookie = "FROM_TYPE=weixin; v=5.5; wechatSESS_ID=29b7e64a25272c96a9823cd84f3d0af918d8da24aeb38ce8; Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjExMjY5MTI5LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNzExMDA0MjcwfQ.fY2Kmztawtm0QFHpkP4AXeB-IqvhUYq1U8lQ7buuT7PZSRvBw1SX1eTOjJTeSShoXm2YqcRBkhxZ-p2DCzXLVE74z3VP85vm4O0cgdA9J8jHpwx2o0YQVOOeCJmJvVpVD0htqD6PxPSjddc-kqXbnj2cZCqVIyHIYFv9cjscYiwHxr1nXWwaUieUXtVaCMDiYokUMGGlR9XPZ0f-0W0dvFRh0D8GBgYFa8jrJ-wkH7MgrW9iR_LIU9QWMsnIV5OJm9zYRFdyIBwDpVca55oRQwo_dQBdnxOlSQiX-0ZeG-k7FWMjrd36HK1YSvFqYzAJ8E06OWNbPAFjji3oNDIjQg; Hm_lvt_7ecd21a13263a714793f376c18038a87=1710848937,1710863114,1710936424,1710997070; Hm_lpvt_7ecd21a13263a714793f376c18038a87=1710997070; SERVERID=e3fa93b0fb9e2e6d4f53273540d4e924|1710997205|1710997066"

data_get_and_store(cookie=cookie,lib=lib)
