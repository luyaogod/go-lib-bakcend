import asyncio
import base64
import aiohttp
import ddddocr
from PIL import Image
import io
import typing

POST_SLEEP=0.9

async def v_jpg_save(image_binary):
    image = Image.open(io.BytesIO(image_binary))
    image.save('output_image.jpg', 'JPEG')


async def header_make(cookie):
    headers = {
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090a13) XWEB/9129 Flue"
    }
    return headers


# ------------------------------------------------------------------------------------
async def code_get(ses: aiohttp.ClientSession, cookie: str):
    url = "https://wechat.v2.traceint.com/index.php/graphql/"
    json = {"operationName": "captcha", "query": "query captcha {\n captcha {\n code\n data\n }\n}"}
    headers = await header_make(cookie)
    async with ses.post(url=url, headers=headers, json=json) as rep:
        ret = await rep.json()
        if 'error' in ret:
            return ''
        if 'data' not in ret:
            return ''
        v_img_base64 = ret['data']['captcha']['data'].split(",")[1]
        v_img_binary = base64.b64decode(v_img_base64)
        return {'v_code': ret['data']['captcha']['code'], 'v_jpg': v_img_binary}


async def code_v(ocr: ddddocr.DdddOcr, img_binary: str):
    result = ocr.classification(img_binary)
    if len(result) != 4:
        return ''
    return result


async def get_and_v(ses: aiohttp.ClientSession, cookie: str, ocr: ddddocr.DdddOcr):
    data = await code_get(cookie=cookie, ses=ses)
    ret = await code_v(ocr, data['v_jpg'])
    return {'captchaCode': data['v_code'], 'captcha': ret}


# interface
async def captcha_get(ses: aiohttp.ClientSession, cookie: str, ocr: ddddocr.DdddOcr):
    """
    返回一个长度为4的验证码以及其对应code的接口
    {'captchaCode':data['v_code'],'captcha':ret}
    """
    count = 0
    ret = {}
    while count < 20:
        data = await get_and_v(cookie=cookie, ses=ses, ocr=ocr)
        if len(data['captcha']) == 4:
            ret = data
            break
        count += 1
    return ret


# ------------------------------------------------------------------------------------

async def get_lib(ses: aiohttp.ClientSession, cookie: str, libId: int):
    json = {"operationName": "libLayout",
            "query": "query libLayout($libId: Int, $libType: Int) {\n userAuth {\n reserve {\n libs(libType: $libType, libId: $libId) {\n lib_id\n is_open\n lib_floor\n lib_name\n lib_type\n lib_layout {\n seats_total\n seats_booking\n seats_used\n max_x\n max_y\n seats {\n x\n y\n key\n type\n name\n seat_status\n status\n }\n }\n }\n }\n }\n}",
            "variables": {"libId": libId}}
    headers = await header_make(cookie)
    url = 'https://wechat.v2.traceint.com/index.php/graphql/'
    await ses.post(url=url, headers=headers, json=json)


async def get_seats(ses: aiohttp.ClientSession, cookie: str, seatKey: str, libId: int, captchaCode: str = '',
                    captcha: str = '', **kwargs) -> int:
    """
    请求座位函数
    :return: 后端响应
    """
    json = {"operationName": "reserueSeat",
            "query": "mutation reserueSeat($libId: Int!, $seatKey: String!, $captchaCode: String, $captcha: String!) {\n userAuth {\n reserve {\n reserueSeat(\n libId: $libId\n seatKey: $seatKey\n captchaCode: $captchaCode\n captcha: $captcha\n )\n }\n }\n}",
            "variables": {"seatKey": seatKey, "libId": libId, "captchaCode": captchaCode, "captcha": captcha}}
    headers = await header_make(cookie)
    url = 'https://wechat.v2.traceint.com/index.php/graphql/'
    async with ses.post(url=url, headers=headers, json=json) as rep:
        rep = await rep.json()
        return rep


# interface
async def one_get_task_group(ses: aiohttp.ClientSession, ocr: ddddocr.DdddOcr, libId: int, seatKey: str, cookie: str):
    """
    单一座位请求操作集合

    :param ses: aiohttp.ClientSession
    :param ocr: ddddocr.DdddOcr
    :param libId: 楼层id
    :param seatKey: 座位key注意不加"." !!!
    :return: False失败 True成功
    """
    print('[进入单任务执行]')
    post_data = {'libId': libId, 'seatKey': seatKey, 'captchaCode': '', 'captcha': ''}
    # 单座位请求循环,每个座位允许验证码错误3次
    count = 0
    while count < 3:
        data = await captcha_get(ses=ses, cookie=cookie, ocr=ocr)
        post_data['captchaCode'] = data['captchaCode']
        post_data['captcha'] = data['captcha']
        print(post_data) #测试
        await get_lib(ses=ses, cookie=cookie, libId=libId)
        rep = await get_seats(ses=ses, cookie=cookie, **post_data)
        print(rep)
        if 'errors' not in rep:
            return 0
        else:
            print(rep)
            if ('该座位已经被人预定了' in rep['errors'][0]['msg']):
                await asyncio.sleep(POST_SLEEP)  #这里也要等待因为主循环会进入下一个任务
                return -1
            if ('操作失败, 您已经预定了座位!' in rep['errors'][0]['msg']):
                return -2
            # if ('请输入验证码' in rep['errors'][0]['msg']):
        count += 1
        await asyncio.sleep(POST_SLEEP)
    return -3  # 验证码错误且尝试了三次


# interface
async def captcha_get_and_seat_get(ocr: ddddocr.DdddOcr, wx_cookie: str,user_id:int, seats: typing.List) :
    """
    多座位顺序请求
    libId – 楼层id
seatKey – 座位key注意不加"." !!!

    :param cookie: cookie
    :param seat_list: 座位列表
    :param ocr: ddddocr.DdddOcr
    :return: False失败 True成功
    """
    result = False
    async with aiohttp.ClientSession() as session:
        for i in seats:
            ret = await one_get_task_group(ses=session,ocr=ocr,cookie=wx_cookie,libId=i['lib_id'],seatKey=i['seat_key'])
            if ret == 0:
                result = True
                break
            if ret ==-2:
                result = True
                break
        await session.close()
        return {"user_id":user_id, "result": result}

if __name__ == "__main__":
    ocr = ddddocr.DdddOcr(show_ad=False)
    data = {'user_id': 1,
             'wx_cookie': 'Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjExMjY5MTI5LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNzE0NjQ0NTIwfQ.PmHPwP680kgR5ipqgNbrwDvKlzZQCUMITsVMrtVoFLe4BU8irKBLpwRaJeFwS7CoHTINhfIlwnMGsVoD5q-6Umvk_RIhzHaahDkU4Ar06SNKhSW8FTvM_9C850nOpNoKO27LkHQ2Ey5t63cLEYBTuVwSGQo2DuUph_VDk5ODHEb7OhcrBMbpIED9q4RX-_86N1W3rbpMeoPvCqEyysRcC9_1i-xhD4B51JPzZ0zd7yvyKUt6zmkmCRbEFt9u6F_c4XQB_-sSQAi3XzmfiOSRwHpBIrFQv-Lk7UWfiMd5254l-yH_NmgCtK9LZODD77iFV8tmf8lKVdo1rMu2tVlVaw; SERVERID=e3fa93b0fb9e2e6d4f53273540d4e924|1714637320|1714637320; ',
             'seats': [{'lib_id': '10072', 'seat_key': '21,11'}, {'lib_id': '10072', 'seat_key': '20,11'},
                       {'lib_id': '10072', 'seat_key': '19,11'}, {'lib_id': '10072', 'seat_key': '18,11'},
                       {'lib_id': '10072', 'seat_key': '17,11'}, {'lib_id': '10072', 'seat_key': '15,11'}]}
    asyncio.run(captcha_get_and_seat_get(ocr=ocr,**data))