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
