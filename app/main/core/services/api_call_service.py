from datetime import datetime

from app.main.core.lib.rest_client import RestClient

from app.main.model.api_model import ApiModel
from app.main.model.api_version_model import ApiVersion
from app.main.model.api_header_model import ApiVersionHeader
from app.main.utils.exceptions import NotFoundError, BadRequestError
from app.main.model.api_key_model import ApiKey
from app.main.model.api_subscription_model import ApiSubscription
from app.main.model.api_request_model import ApiRequest

from app.main import db


class ApiCallService:
    def __init__(self, rest_client: RestClient):
        self.rest_client = rest_client

    def call_get(self, api_id: int, version: str, params: str, api_key: str):
        subscription_id = self.verify_api_key(api_key)

        subscription = self.verify_subscription(subscription_id, api_id)

        base_url = self.__get_api_version_base_url(api_id, version)

        headers = self.__get_api_version_headers(api_id, version)

        request_url = f"{base_url}/{params}"

        request_at = datetime.now()

        response, status = self.rest_client.get(request_url, headers)

        response_at = datetime.now()

        response_time = (response_at - request_at).seconds

        request_method = "GET"

        user_id = subscription.user_id

        request_body = ""

        response_body = str(response)

        new_request = ApiRequest(
            api_id=api_id,
            api_version=version,
            user_id=user_id,
            api_key=api_key,
            subscription_id=subscription_id,
            request_url=request_url,
            request_method=request_method,
            request_body=request_body,
            response_body=response_body,
            request_at=request_at,
            response_at=response_at,
            response_time=response_time,
            http_status=status,
        )

        db.session.add(new_request)
        db.session.commit()

        self.decrement_subscription_requests(subscription_id)

        return response, status

    def call_post(
        self, api_id: int, version: str, params: str, api_key: str, body: str
    ):
        subscription_id = self.verify_api_key(api_key)

        subscription = self.verify_subscription(subscription_id, api_id)

        base_url = self.__get_api_version_base_url(api_id, version)

        headers = self.__get_api_version_headers(api_id, version)

        request_url = f"{base_url}/{params}"

        request_at = datetime.now()

        response, status = self.rest_client.post(request_url, headers, body)

        response_at = datetime.now()

        response_time = (response_at - request_at).seconds

        request_method = "POST"

        user_id = subscription.user_id

        request_body = str(body)

        response_body = str(response)

        new_request = ApiRequest(
            api_id=api_id,
            api_version=version,
            user_id=user_id,
            api_key=api_key,
            subscription_id=subscription_id,
            request_url=request_url,
            request_method=request_method,
            request_body=request_body,
            response_body=response_body,
            request_at=request_at,
            response_at=response_at,
            response_time=response_time,
            http_status=status,
        )

        db.session.add(new_request)
        db.session.commit()

        self.decrement_subscription_requests(subscription_id)

        return response, status

    def call_patch(
        self, api_id: int, version: str, params: str, api_key: str, body: str
    ):
        subscription_id = self.verify_api_key(api_key)

        subscription = self.verify_subscription(subscription_id, api_id)

        base_url = self.__get_api_version_base_url(api_id, version)

        headers = self.__get_api_version_headers(api_id, version)

        request_url = f"{base_url}/{params}"

        request_at = datetime.now()

        response, status = self.rest_client.patch(request_url, headers, body)

        response_at = datetime.now()

        response_time = (response_at - request_at).seconds

        request_method = "PATCH"

        user_id = subscription.user_id

        request_body = str(body)

        response_body = str(response)

        new_request = ApiRequest(
            api_id=api_id,
            user_id=user_id,
            api_key=api_key,
            subscription_id=subscription_id,
            api_version=version,
            request_url=request_url,
            request_method=request_method,
            request_body=request_body,
            response_body=response_body,
            request_at=request_at,
            response_at=response_at,
            response_time=response_time,
            http_status=status,
        )

        db.session.add(new_request)
        db.session.commit()

        self.decrement_subscription_requests(subscription_id)

        return response, status

    def call_delete(self, api_id: int, version: str, params: str, api_key: str):
        subscription_id = self.verify_api_key(api_key)

        subscription = self.verify_subscription(subscription_id, api_id)

        base_url = self.__get_api_version_base_url(api_id, version)

        headers = self.__get_api_version_headers(api_id, version)

        request_url = f"{base_url}/{params}"

        request_at = datetime.now()

        response, status = self.rest_client.delete(request_url, headers)

        response_at = datetime.now()

        response_time = (response_at - request_at).seconds

        request_method = "DELETE"

        user_id = subscription.user_id

        request_body = ""

        response_body = str(response)

        new_request = ApiRequest(
            api_id=api_id,
            user_id=user_id,
            api_key=api_key,
            api_version=version,
            subscription_id=subscription_id,
            request_url=request_url,
            request_method=request_method,
            request_body=request_body,
            response_body=response_body,
            request_at=request_at,
            response_at=response_at,
            response_time=response_time,
            http_status=status,
        )

        db.session.add(new_request)
        db.session.commit()

        self.decrement_subscription_requests(subscription_id)

        return response, status

    def verify_api_key(self, api_key: str):
        api_key_data = ApiKey.query.filter_by(key=api_key).first()

        if api_key_data is None:
            raise BadRequestError("Invalid API key")

        if api_key_data.status != "active":
            raise BadRequestError("API key is not active")

        return api_key_data.subscription_id

    def verify_subscription(self, subscription_id: int, api_id: int):
        subscription = ApiSubscription.query.filter_by(
            id=subscription_id, api_id=api_id
        ).first()

        if subscription is None:
            raise BadRequestError("Invalid subscription")

        if subscription.status != "active":
            raise BadRequestError("Subscription is not active")

        expired = subscription.end_date < datetime.now()

        if expired:
            raise BadRequestError("Subscription has expired")

        no_remaining_requests = subscription.max_requests <= 0

        if no_remaining_requests:
            raise BadRequestError(
                "Subscription has no requests left, Please renew subscription"
            )

        return subscription

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

    def decrement_subscription_requests(self, subscription_id: int):
        subscription = ApiSubscription.query.filter_by(id=subscription_id).first()

        subscription.max_requests -= 1

        db.session.commit()
