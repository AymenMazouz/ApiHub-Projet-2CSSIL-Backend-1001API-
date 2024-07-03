from app.main.core.lib.rest_client import RestClient
from app.main.model.api_model import ApiModel
from app.main.model.api_version_model import ApiVersion
from app.main.model.api_header_model import ApiVersionHeader
from app.main.utils.exceptions import NotFoundError, BadRequestError


class ApiTestsService:

    def __init__(self, rest_client: RestClient):
        self.rest_client = rest_client

    def test_get(self, api_id: int, version: str, params: str):
        base_url = self.__get_api_version_base_url(api_id, version)

        headers = self.__get_api_version_headers(api_id, version)

        url = f"{base_url}/{params}"

        response = self.rest_client.get(url, headers)

        return response

    def test_post(self, api_id: int, version: str, params: str, data: dict):
        base_url = self.__get_api_version_base_url(api_id, version)

        headers = self.__get_api_version_headers(api_id, version)

        url = f"{base_url}/{params}"

        response = self.rest_client.post(url, headers, data)

        return response

    def test_patch(self, api_id: int, version: str, params: str, data: dict):
        base_url = self.__get_api_version_base_url(api_id, version)

        headers = self.__get_api_version_headers(api_id, version)

        url = f"{base_url}/{params}"

        response = self.rest_client.patch(url, headers, data)

        return response

    def test_delete(self, api_id: int, version: str, params: str):
        base_url = self.__get_api_version_base_url(api_id, version)

        headers = self.__get_api_version_headers(api_id, version)

        url = f"{base_url}/{params}"

        response = self.rest_client.delete(url, headers)

        return response

    def __get_api_version_base_url(self, api_id: int, version: str):
        api_data = ApiModel.query.filter_by(id=api_id).first()

        if api_data is None:
            raise NotFoundError("API not found")

        if api_data.status != "active":
            raise BadRequestError("API is not active")

        version_data = ApiVersion.query.filter_by(
            api_id=api_id, version=version
        ).first()

        if version_data is None:
            raise NotFoundError("API version not found")

        if version_data.status != "active":
            raise BadRequestError("API version is not active")

        return version_data.base_url

    def __get_api_version_headers(self, api_id: int, version: str):
        headers = ApiVersionHeader.query.filter_by(
            api_id=api_id, api_version=version
        ).all()

        headers_dict = {header.key: header.value for header in headers}

        return headers_dict
