
import aiohttp
from settings import mlog as log
from urllib.parse import urlencode
from hashlib import md5
import base64
import ddddocr

class Ocr():
    """
    ocr_choice: 1百度 2超级鹰 3本地ddddocr
    """
    def __init__(
        self,
        ocr_choice:str, 
        ses:aiohttp.ClientSession
    ) -> None:
        self._choice = ocr_choice
        self._ses = ses

        self._baidu_API_KEY = "Ne7sclOS3DID6aocoIATfLmI"
        self._baidu_SECRET_KEY = "3nGpP4tkqfBx6vr15nUuBPnqogFQnSRm"

        self._chaoJiYing_username = "mariokkm"
        self._ChaoJiYing_password = "maluyao123"
        self._ChoaJiYing_softId = "961185"
        
        if ocr_choice not in [1,2,3]:
            raise ValueError('错误参数')
        elif ocr_choice == 3:
            self._docr = ddddocr.DdddOcr(show_ad=False)
            self._docr.set_ranges(6)

    #Baidu--
    async def get_access_token(self):
        """
        使用 AK，SK 生成鉴权签名（Access Token）
        :return: access_token，或是None(如果错误)
        """
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": self._baidu_API_KEY, "client_secret": self._baidu_SECRET_KEY}
        async with self._ses.post(url, params=params) as response:
            resp_json = await response.json()
            return str(resp_json.get("access_token"))

    async def baidu_ocr(self, img_b64:str, access_token:str):
        url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token={access_token}"
        
        payload = urlencode({"image": img_b64 })
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        async with self._ses.post(url, headers=headers, data=payload) as response:
            resp_json = await response.json()
            print(resp_json)
            return resp_json

    #超级鹰--
    async def chaojiy_ocr(self, base64_str:str)->str | None:
        try:
            pw = self._ChaoJiYing_password
            pw_bytes = pw.encode('utf-8')
            pw_5 = md5(pw_bytes).hexdigest()
            payload= {
                    'user': self._chaoJiYing_username,
                    'pass2': pw_5,
                    'softid': self._ChoaJiYing_softId,
                    'codetype': 1004,
                    'file_base64':base64_str
                }
            headers = {
                    'Connection': 'Keep-Alive',
                    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
                }
            url = 'http://upload.chaojiying.net/Upload/Processing.php'
            async with self._ses.post(url, headers=headers, data=payload) as response:
                resp_json = await response.json()
                if "pic_str" in resp_json:
                    log.debug(resp_json['pic_str'])
                    return resp_json['pic_str']
                else:
                    return None
        except Exception as e:
            log.warning(f'超级鹰验证接口报错：{e}')
            return None

    #本地识别ddddocr-
    def ddddd_v(self, img_b64: str):
        """二维码识别"""
        v_img_binary = base64.b64decode(img_b64)
        result = self._docr.classification(v_img_binary)
        return result

    #API
    async def ocr_v(self, img_b64: str)->str|None:
        """识别接口，传入base64编码字符串"""
        if self._choice == 1:
            token = await self.get_access_token()
            ret = await self.baidu_ocr(img_b64, token)
            return ret
        
        elif self._choice == 2:
            ret = await self.chaojiy_ocr(img_b64)
            return ret

        elif self._choice == 3:
            ret = self.ddddd_v(img_b64)
            return ret