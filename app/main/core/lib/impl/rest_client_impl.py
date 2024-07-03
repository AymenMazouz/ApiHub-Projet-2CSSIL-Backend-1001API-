import requests
import json
from typing import Dict, Tuple
from app.main.core.lib.rest_client import RestClient


class RestClientImpl(RestClient):
    def get(self, url, headers) -> Tuple[Dict, int]:
        response = requests.get(url, headers=headers, timeout=10)
        return response.json(), response.status_code

    def post(self, url, headers, data) -> Tuple[Dict, int]:
        if not isinstance(data, str):
            data = json.dumps(data)
        response = requests.post(url, headers=headers, data=data, timeout=10)

        return response.json(), response.status_code

    def delete(self, url, headers) -> Tuple[Dict, int]:
        response = requests.delete(url, headers=headers, timeout=10)
        return response.json(), response.status_code

    def patch(self, url, headers, data) -> Tuple[Dict, int]:
        if not isinstance(data, str):
            data = json.dumps(data)
        response = requests.patch(url, headers=headers, data=data, timeout=10)
        return response.json(), response.status_code
