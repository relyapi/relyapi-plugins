from urllib.parse import urlparse, parse_qs

import requests
from cachetools import TTLCache
from relyapi.plugin import BasePlugin, RequestModel
from relyapi.utils import replace_cookie, replace_query_param, gen_md5
from tenacity import retry, stop_after_attempt, wait_exponential

retry_strategy = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)


class TaobaoPlugin(BasePlugin):
    domain = "h5api.m.taobao.com"
    use_proxy = True
    cache = TTLCache(maxsize=100, ttl=3600)

    @retry_strategy
    def get_h5_tk(self):
        headers = {
            "f-refer": "wv_h5",
            "Accept": "*/*",
            "Sec-Fetch-Site": "same-site",
            "f-pTraceId": "WVNet_WV_4-9-246",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Fetch-Mode": "no-cors",
            "Cookie": "cna=0aOTHh10cnMCAWfbuzIeA06I; lid=fovegage; wk_unb=UUphyu7pUmUAVMK2jA%3D%3D; wk_cookie2=12d88e80178c146e28958fdc186e216e; dnk=fovegage; uc3=nk2=Bd%2F84gqLDpc%3D&id2=UUphyu7pUmUAVMK2jA%3D%3D&vt3=F8dD3ijAVgwKXRQRs8k%3D&lg2=VFC%2FuZ9ayeYq2g%3D%3D; tracknick=fovegage; uc4=id4=0%40U2grEagtest0ESyCKKKKa3hxFsYykcOz&nk4=0%40B1PKErRskKL0aAkCJjIACHNOWQ%3D%3D; _l_g_=Ug%3D%3D; unb=2200722477427; lgc=fovegage; cookie1=AnfpadUfSWbDmHKKzE28SbFtt%2BZZ1E%2BMLdR1ka%2BN77M%3D; login=true; cookie17=UUphyu7pUmUAVMK2jA%3D%3D; cookie2=13b52cad1e32de7cb26755ddabbf9a7c; _nk_=fovegage; sgcookie=E100lv%2FteReCDiyDZPq%2FWG9D2BGhV9sQa7bgql8CfRXp5coNuaQfCLn7poD5XHumylsFrlCUeZJ0Zo%2Bp0zEmpJd78%2BoN1WKILt6VV9a5qWNxBnRluxOQcW56z9UZpjjcFnQM; cancelledSubSites=empty; t=099f7080c3ec0046dc2b554a2e12659c; sg=e76; csg=2ffb1c61; sn=; _tb_token_=eeee75e33e135; xlly_s=1; x5sectag=851848; x5sec=7b22733b32223a2261303038626434323332653765366363222c22617365727665723b33223a22307c434f443778625547454b2f2b34615547476738794d6a41774e7a49794e4463334e4449334f7a496f674151772b6265457867493d227d; mtop_partitioned_detect=1; _m_h5_tk=67499fb65972aac94322a1f59ebdc320_1722918574799; _m_h5_tk_enc=5cbec671bdd9afa8afc4dc427b824b2a; tfstk=fUzx9ZDZi_dA7njglSsoSUE1TKfuMrFqy-PBSADDf8e8LJLGgo2g2fwuBV0g1tyTWYwvSoV01Ch_EqiamADmBVFap_Xh-wV4gVucK9bnBRJ_kVk1SVtm5WCI59Xhr3AS0t0_jbO0-4FSUfh6hVwsFUGIFjG6cRMSVXGHhVg_C71-TfYXGFijFYTrzUkNfvYTf-wcElRqmFT_kNoxp7xM5Fa-Mmn8GYhntzhxDvnJbJIuJWNb8fUNOhHTTowmaRQde4aYHri-WNLroWE7H0EABUnzVWzs2uWpYWPbHkiQlaCS2rPnlYUN_Fkbm5aiXr6Bsxa4nznU7KBoIkVul0eCEUeZXoZIlPBdPgWz-y3uopDKsn1Rwh-Zcb4dC3tKrI5SAbHhZ-twb0KEwvfRch-Zcbl-K_0ybhoJY; isg=BPn5mdUcu1k6QmSCLjCXrKtrCGPTBu24r3xwRRsucyCKohk0Y1UoiRK8JaZUR4Xw",
            "language": "zh-Hans",
            "region": "CN",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 AliApp(EA/8.29.0) WindVane/8.7.2 UT4Aplus/0.0.7 1125x2436 WK",
            "Referer": "https://detail.tmall.com/"
        }
        r = requests.get(
            "https://h5api.m.taobao.com/h5/mtop.cainiao.address.ua.china.town.list/1.0/?jsv=2.5.7&appKey=12574478",
            headers=headers)
        r = dict(r.cookies)
        return {
            '_m_h5_tk': r['_m_h5_tk'],
            '_m_h5_tk_enc': r['_m_h5_tk_enc']
        }

    def sign(self, key, millis, data, app_key="12574478"):
        """
        :param key: _m_h5_tk 前半段
        :param millis:  11位时间戳
        :param data: 请求接口淘宝接口的data数据
        :param app_key: 固定
        :return:
        """
        _sign_str = "{0}&{1}&{2}&{3}".format(key, millis, app_key, data)
        _sign_str = gen_md5(_sign_str)
        return _sign_str

    def do_sign(self, ts: int, body: str) -> dict:
        if self.cache.get('h5_tk'):
            h5_tk = self.cache.get('h5_tk')
        else:
            h5_tk = self.get_h5_tk()
            self.cache['h5_tk'] = h5_tk

        _m_h5_tk, _m_h5_tk_enc = h5_tk['_m_h5_tk'], h5_tk['_m_h5_tk_enc']
        sign = self.sign(str(_m_h5_tk).split('_')[0], ts, body)
        return {
            'sign': sign,
            "ts": ts,
            "_m_h5_tk_enc": _m_h5_tk_enc,
            "_m_h5_tk": _m_h5_tk
        }

    def invoke(self, url, method, headers, body=None) -> RequestModel:
        """
        {"id":"920151030898","detail_v":"3.3.2","exParams":"{\"id\":\"920151030898\",\"pvid\":\"1ca2c056-933f-43bb-ab10-c20fe888f4b2\",\"scm\":\"1007.40986.420852.520371\",\"skuId\":\"5965041306559\",\"spm\":\"a21bo.jianhua/a.201876.d1.5af92a89DbvnMC\",\"utparam\":\"{\\\"abid\\\":\\\"520371\\\",\\\"item_ctr\\\":0,\\\"x_object_type\\\":\\\"item\\\",\\\"pc_pvid\\\":\\\"1ca2c056-933f-43bb-ab10-c20fe888f4b2\\\",\\\"item_cvr\\\":0,\\\"mix_group\\\":\\\"\\\",\\\"pc_scene\\\":\\\"20001\\\",\\\"item_ecpm\\\":0,\\\"aplus_abtest\\\":\\\"d0f6f2453320cd2e232fa957203ab976\\\",\\\"tpp_buckets\\\":\\\"30986#420852#module\\\",\\\"x_object_id\\\":920151030898,\\\"ab_info\\\":\\\"30986#420852#-1#\\\"}\",\"xxc\":\"home_recommend\",\"queryParams\":\"id=920151030898&ltk2=17532534875665q3kkttoe73w8llli4zufb&pvid=1ca2c056-933f-43bb-ab10-c20fe888f4b2&scm=1007.40986.420852.520371&skuId=5965041306559&spm=a21bo.jianhua%2Fa.201876.d1.5af92a89DbvnMC&utparam=%7B%22abid%22%3A%22520371%22%2C%22item_ctr%22%3A0%2C%22x_object_type%22%3A%22item%22%2C%22pc_pvid%22%3A%221ca2c056-933f-43bb-ab10-c20fe888f4b2%22%2C%22item_cvr%22%3A0%2C%22mix_group%22%3A%22%22%2C%22pc_scene%22%3A%2220001%22%2C%22item_ecpm%22%3A0%2C%22aplus_abtest%22%3A%22d0f6f2453320cd2e232fa957203ab976%22%2C%22tpp_buckets%22%3A%2230986%23420852%23module%22%2C%22x_object_id%22%3A920151030898%2C%22ab_info%22%3A%2230986%23420852%23-1%23%22%7D&xxc=home_recommend\",\"domain\":\"https://item.taobao.com\",\"path_name\":\"/item.htm\",\"pcSource\":\"pcTaobaoMain\",\"appKey\":\"3q2+7wX9z8JkLmN1oP5QrStUvWxYzA0B\",\"refId\":\"OQLAXmC4wfP0IakLEpSUmju3UcFSOfCMe1183XEZ6KI=\",\"nonce\":\"fui4Y5l6gb2FCEKCsU3/8QvyLEyC24NuxlShO5YNUCo=\",\"feTraceId\":\"e0c89dce-3ff2-4803-bc8c-7d07a0dfa220\"}"}
        :param url:
        :param method:
        :param headers:
        :param body:
        :return:
        """
        parsed = urlparse(url)

        # 获取查询参数为字典
        query_params = parse_qs(parsed.query)
        data = query_params["data"][0]
        ts = int(query_params["t"][0])

        sign = self.do_sign(ts, data)

        sign_url = replace_query_param(url, 'sign', sign['sign'])
        ts_url = replace_query_param(sign_url, 't', sign['ts'])
        tk_enc_ck = replace_cookie(headers['cookie'], '_m_h5_tk_enc', sign['_m_h5_tk_enc'])
        h5_tk_ck = replace_cookie(tk_enc_ck, '_m_h5_tk', sign['_m_h5_tk'])

        headers['cookie'] = h5_tk_ck
        return RequestModel(
            url=ts_url,
            method=method,
            headers=headers
        )


if __name__ == '__main__':
    headers = {
        # 'bx-umidtoken': 'T2gA7hdNyYEDlQNqHL5qBBLTO0gnaw4WFkpy_fBEFlMhde4kLg_6AA1TCfe6M2-ZRR8=',
        # 'x-pipu2': "h%7Bdufj%7Cvljommtc%7Dv%2C(8%2C8%2F)0%3E!%3A%26'9%3A%606%2B%2F%2Fg*1%3B%3A3%2B%3D%3C*g*1%3B%3A3%2B%3D%3C*g*1%3B%3A3%2B%3D%3C*go%7Bo%7B",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://item.taobao.com",
        "referer": "https://item.taobao.com",
        "cookie": 'thw=cn; wk_cookie2=19f87593975a3f9bd7b260a1fe92ce8f; wk_unb=UoTUOqkyuVGCXA%3D%3D; aui=1580993065; cookie2=125d44a46272791eaca7fca31a273a71; t=7d19e9bcd1bed6fb395e5de8c45df1a8; _tb_token_=71b1feebe5b63; sgcookie=E100UJeih4P9%2F9CO406ZMYbow8YaHdbfuSSX3ulinUQeZogBMdt5B%2FsLIaOTQaKFLnJF6yAIyDZCmbQR%2BQZDc3KX8EFUKwKMIrjCobQ0L5Psg7EMqJqXYflqDwHyHSfRelc5SL7qvFFIYWKyIlYJp8e9BA%3D%3D; tracknick=; xlly_s=1; mtop_partitioned_detect=1; _m_h5_tk=d669faa1bbf906fc5d71fa21b7f1e8b5_1753256638922; _m_h5_tk_enc=6d236082ebb8a84a9391a4149939b4ae; sca=289541c2; bxuab=0; isg=BHh4lepuZFtoWoggSu8cnp2mSSYK4dxrgA7eBLLp2rNozRm3WvFg-ozlgcX9m5RD; tfstk=gX6-Zfa6Lr4l8hWJmgPmxj9csxE0SSjPDaSsKeYoOZQArG1kZMTHpwQdJUAQzLXdkaj1ZQjCKH6pUtfoKU4ypM_MpP4gIRjP4LJQSPjv2Z59dHwHRSA72fig2P4gI-VScpU8Sw23xwwvYEtSFpG7DmT2x49BPBgjGhTXdpMWAmiXjhMSdp_CcoKele9BNwObDHlr20LnVeHdwg-13lo9VvMCH3d7igTjdnWv2QL1VtkIdf-JwFsWlzgkOjRfYBBEYvdhV17efag7JeWAcT115rckP1Kdj6Q_xb-D9TJvRTwZXE6RvtdPi4GWXLLJ1TO_plI6OsBvETaE_ijvPCpciSzktLQR_FR7gr7dDUbCeIg8oefGmTOA5rDA8BCCEK67lRIrROXOSv0MWHc7DohETQt4LZheVvptCUxvSocmTXRD0nLgDohETQt2DFq0nXlein5..',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    }

    body = {
        "jsv": "2.7.5",
        "appKey": "12574478",
        "t": "1753266490635",
        "sign": "a1926a06b852e0e4467e9fd3db3a4b94",
        "api": "mtop.taobao.pcdetail.data.get",
        "v": "1.0",
        "isSec": "0",
        "ecode": "0",
        "timeout": "10000",
        "ttid": "2022@taobao_litepc_9.17.0",
        "AntiFlood": "true",
        "AntiCreep": "true",
        "dataType": "json",
        "valueType": "string",
        "type": "json",
        "data": {"id": "914207844760", "detail_v": "3.3.2",
                 "exParams": "{\"id\":\"914207844760\",\"pvid\":\"ea5ff2f2-b3fa-409a-a0e1-97065611df52\",\"scm\":\"1007.40986.420852.520372\",\"skuId\":\"5038612183860\",\"spm\":\"a21bo.jianhua/a.201876.d13.5af92a89CG15f1\",\"utparam\":\"{\\\"abid\\\":\\\"520372\\\",\\\"item_ctr\\\":0,\\\"x_object_type\\\":\\\"item\\\",\\\"pc_pvid\\\":\\\"ea5ff2f2-b3fa-409a-a0e1-97065611df52\\\",\\\"item_cvr\\\":0,\\\"mix_group\\\":\\\"\\\",\\\"pc_scene\\\":\\\"20001\\\",\\\"item_ecpm\\\":0,\\\"aplus_abtest\\\":\\\"cb98573c80be78070270b13b66228028\\\",\\\"tpp_buckets\\\":\\\"30986#420852#module\\\",\\\"x_object_id\\\":677811311950,\\\"ab_info\\\":\\\"30986#420852#-1#\\\"}\",\"xxc\":\"home_recommend\",\"queryParams\":\"id=677811311950&ltk2=1753266480249a6wq1tn94ypmp5s0a6usqq&pvid=ea5ff2f2-b3fa-409a-a0e1-97065611df52&scm=1007.40986.420852.520372&skuId=5038612183860&spm=a21bo.jianhua%2Fa.201876.d13.5af92a89CG15f1&utparam=%7B%22abid%22%3A%22520372%22%2C%22item_ctr%22%3A0%2C%22x_object_type%22%3A%22item%22%2C%22pc_pvid%22%3A%22ea5ff2f2-b3fa-409a-a0e1-97065611df52%22%2C%22item_cvr%22%3A0%2C%22mix_group%22%3A%22%22%2C%22pc_scene%22%3A%2220001%22%2C%22item_ecpm%22%3A0%2C%22aplus_abtest%22%3A%22cb98573c80be78070270b13b66228028%22%2C%22tpp_buckets%22%3A%2230986%23420852%23module%22%2C%22x_object_id%22%3A677811311950%2C%22ab_info%22%3A%2230986%23420852%23-1%23%22%7D&xxc=home_recommend\",\"domain\":\"https://item.taobao.com\",\"path_name\":\"/item.htm\",\"pcSource\":\"pcTaobaoMain\",\"appKey\":\"3q2+7wX9z8JkLmN1oP5QrStUvWxYzA0B\",\"refId\":\"qpwf1ia3TROBr4pZeesSCnEuwmNBRqZmi73VCLc/9ac=\",\"nonce\":\"Qyb3y3WsGXsF7HK8wMFVtSz0yqIjkyfkmpeGBpV6CE4=\",\"feTraceId\":\"2cc93268-c36d-469a-82e8-5d95cfed039a\"}"}
    }

    url = 'https://h5api.m.taobao.com/h5/mtop.taobao.pcdetail.data.get/1.0/'

    plugin = TaobaoPlugin()
    result = plugin.invoke(url,method='GET', headers=headers, body=None)
    # 需要这样的一个客户端  然后
    resp = client.get(url=url, params=body, headers=headers)
