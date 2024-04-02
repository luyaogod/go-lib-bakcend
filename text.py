import aiohttp
import asyncio
from datetime import datetime

url = 'http://wechat.v2.traceint.com/index.php/graphql/'

headers = {
    "Cookie": "FROM_TYPE=weixin; v=5.5; Hm_lvt_7ecd21a13263a714793f376c18038a87=1711883379,1711941144,1711965201,1712041355; Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjExMjY5MTI5LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNzEyMDQ5MTE1fQ.TDoAGSopwbHqAEZ_EAPOY4RUCjYkndeDLyk-v-cHlJOI56WbAOYRYNvBd3RY0iloXksBOJBI4q28MzyEoQN2P--NpaVSGbEz0GfwdbvuqLBqQu2u4VsxBHPNv0B-nsCxtK5cxvPn1OllHES0kGamBr7NoapFdw4D9CyiWVLKENrpfvR9abUbT2P8v2Yw8Sis6KMXmRGzhWYyV1ULYL_BskkJh6skswLiLy94YPf-bA0k7hUnemD-1lFViBbItpN_NYyM1cXPYfR4dwB1KFouGV2IiKpm60cQe9PilCzadHkwn0RJFmHeqkTwQnwEs1yCnYzxbA-6iWoYuuxGpglKyQ; Hm_lpvt_7ecd21a13263a714793f376c18038a87=1712042577; wechatSESS_ID=4e93f6802a1e935813cce6daedf6321941a9ce17978b81ee; SERVERID=e3fa93b0fb9e2e6d4f53273540d4e924|1712047300|1712047296",
}

json = {"operationName":"index","query":"query index {\n userAuth {\n tongJi {\n rank\n allTime\n dayTime\n }\n config: user {\n feedback: getSchConfig(fields: \"adm.feedback\")\n }\n }\n}"}

async def cookie_test():
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url,headers=headers,json=json,) as rep:
            data = await rep.text()
            if "errors" not in data:
                print("[cookie有效]",data)
                return True
            else:
                print("[cookie失效]")
                return False

async def main():
    while True:
        ret = await cookie_test()
        if not ret:
            break
        await asyncio.sleep(60)
    print("[测试结束]", datetime.now())

if __name__ == "__main__":
    print("[测试开始]", datetime.now())
    asyncio.run(cookie_test())
