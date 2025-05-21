import hashlib
import os
import time
from urllib.parse import urlencode

from dotenv import load_dotenv
from httpx import AsyncClient


load_dotenv()

SHUIDI_PNAME = os.getenv("shuidi_pname")
SHUIDI_PKEY = os.getenv("shuidi_pkey")

def create_api_adapter(url, pname=SHUIDI_PNAME, pkey=SHUIDI_PKEY):

    return ApiAdapter(url, pname, pkey)

def create_search_api_adapter(pname=SHUIDI_PNAME, pkey=SHUIDI_PKEY):

    return SearchApiAdapter(pname, pkey)

class ApiAdapter:
    def __init__(self, url, pname, pkey):
        self.url = url
        self.pname = pname
        self.pkey = pkey


    async def _invoke(self, params=None):
        filtered_params = {k: v for k, v in params.items() if v is not None}
        api_params = urlencode(filtered_params)

        ptime = int(time.time() * 1000)
        m = hashlib.md5()
        m.update((self.pkey + '_' + str(ptime) + '_' + self.pkey).encode('utf-8'))
        vkey = m.hexdigest()

        api_url = f'{self.url}?{api_params}&pname={self.pname}&ptime={ptime}&vkey={vkey}'

        async with AsyncClient() as client:
            response = await client.get(api_url)
            return response.json()


    async def invoke(self, params=None):

        response = await self._invoke(params)
        return self._on_response(response)

    def _on_response(self, response):
        return response


class SearchApiAdapter(ApiAdapter):

    def __init__(self, pname, pkey):
        super().__init__(url='http://api.shuidi.cn/utn/action/search/SeniorSearch', pname=pname, pkey=pkey)

    def _on_response(self, response):
        # 控制响应大小，只保留接口返回的必要数据
        keys_to_copy = ['companyName','creditNo','establishDate','legalPerson', 'capital', 'companyStatusStr']
        data = response.get('data')
        if data:
            data_list = data.get('data_list')
            if data_list:
                new_data_list = []
                for row in data_list:
                    new_row = {k: row[k] for k in keys_to_copy}
                    new_data_list.append(new_row)
                data['data_list'] = new_data_list
        response['data'] = data
        #删除多余的status,与其他api接口统计返回格式
        response.pop('status', None)
        return response
