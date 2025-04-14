import hashlib
import os
import time
from urllib.parse import urlencode

from dotenv import load_dotenv
from httpx import AsyncClient
from loguru import logger

load_dotenv()

SHUIDI_PNAME = os.getenv("shuidi_pname")
SHUIDI_PKEY = os.getenv("shuidi_pkey")

class ApiAdapter:
    def __init__(self, url):
        self.url = url

    async def _invoke(self,params=None):
        filtered_params = {k: v for k, v in params.items() if v is not None}
        api_params = urlencode(filtered_params)

        ptime = int(time.time() * 1000)
        m = hashlib.md5()
        m.update((SHUIDI_PKEY + '_' + str(ptime) + '_' + SHUIDI_PKEY).encode('utf-8'))
        vkey = m.hexdigest()

        api_url = f'{self.url}?{api_params}&pname={SHUIDI_PNAME}&ptime={ptime}&vkey={vkey}'

        logger.debug(f'api url: {api_url}')

        async with AsyncClient() as client:
            response = await client.get(api_url)
            return response.json()


    async def invoke(self, params=None):
        response = await self._invoke(params)
        return self._on_response(response)

    def _on_response(self, response):
        logger.debug(f'response: {response}')
        return str(response)


class SearchApiAdapter(ApiAdapter):

    def __init__(self):
        super().__init__('http://api.shuidi.cn/utn/action/search/SeniorSearch')

    def _on_response(self, response):
        # 控制响应大小，只保留接口返回的必要数据
        keys_to_copy = ['companyName','creditNo','establishDate','legalPerson', 'capital','companyStatusStr']
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
        return str(response)
