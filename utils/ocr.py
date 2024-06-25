
import base64
import ddddocr

class Ocr():
    """
    ocr_choice: 1百度 2超级鹰 3本地ddddocr
    """
    def __init__(
        self,
    ) -> None:
        self._docr = ddddocr.DdddOcr(show_ad=False)
        self._docr.set_ranges(6) #设置识别范围

    #本地识别ddddocr-
    def ddddd_v(self, img_b64: str):
        """二维码识别"""
        v_img_binary = base64.b64decode(img_b64)
        result = self._docr.classification(v_img_binary)
        return result

    #API
    async def ocr_v(self, img_b64: str)->str|None:
        """识别接口，传入base64编码字符串"""
        ret = self.ddddd_v(img_b64)
        return ret