from app.main.model.api_version_model import ApiVersion
from app.main.model.api_model import ApiModel
from app.main.model.api_request_model import ApiRequest
from app.main.model.api_version_endpoint_model import ApiVersionEndpoint
from app.main.model.api_header_model import ApiVersionHeader
from app.main import db
from app.main.utils.exceptions import NotFoundError, BadRequestError
from typing import Dict
from app.main.utils.roles import Role
from sqlalchemy import func


class ApiVersionService:
    def create_api_version(self, api_id: int, supplier_id: int, data: dict):
        api = ApiModel.query.filter_by(id=api_id, supplier_id=supplier_id).first()
        if api is None:
            raise NotFoundError("No API found with id: {}".format(api_id))

        if ApiVersion.query.filter_by(
            api_id=api_id, version=data.get("version")
        ).first():
            raise BadRequestError("API version already exists")

        api_version = ApiVersion(
            api_id=api_id,
            version=data.get("version"),
            base_url=data.get("base_url"),
            status="active",
        )

        db.session.add(api_version)
        db.session.commit()

        endpoints = data.get("endpoints", [])

        for endpoint in endpoints:
            endpoint = ApiVersionEndpoint(
                api_id=api_id,
                version=api_version.version,
                endpoint=endpoint.get("url"),
                method=endpoint.get("method"),
                description=endpoint.get("description"),
                request_body=endpoint.get("request_body"),
                response_body=endpoint.get("response_body"),
            )
            db.session.add(endpoint)

        db.session.commit()

        headers = data.get("headers", [])

        for header in headers:
            header = ApiVersionHeader(
                api_id=api_id,
                api_version=api_version.version,
                key=header.get("key"),
                value=header.get("value"),
            )
            db.session.add(header)

        db.session.commit()

    def get_api_versions(self, api_id: int, query_params: Dict):
        status = query_params.get("status")

        query = ApiVersion.query.filter_by(api_id=api_id)

        query = query.filter_by(status=status) if status else query

        versions = query.all()

        return [
            {
                "version": version.version,
                "status": version.status,
                "created_at": version.created_at.isoformat(),
                "updated_at": version.updated_at.isoformat(),
            }
            for version in versions
        ]

    def get_api_version(self, api_id: int, version: str):
        version_data = (
            db.session.query(ApiVersion, ApiModel)
            .filter(
                ApiVersion.api_id == api_id,
                ApiVersion.version == version,
                ApiModel.id == api_id,
            )
            .first()
        )

        if version_data is None:
            raise NotFoundError(
                "No API version found with id: {} and version: {}".format(
                    api_id, version
                )
            )

        endpoints = ApiVersionEndpoint.query.filter_by(
            api_id=api_id, version=version
        ).all()

        average_response_time = (
            db.session.query(func.avg(ApiRequest.response_time))
            .filter(ApiRequest.api_version == version)
            .filter(ApiRequest.api_id == api_id)
            .scalar()
        )

        return {
            "version": version_data.ApiVersion.version,
            "status": version_data.ApiVersion.status,
            "average_response_time": average_response_time,
            "created_at": version_data.ApiVersion.created_at.isoformat(),
            "updated_at": version_data.ApiVersion.updated_at.isoformat(),
            "api": {
                "id": version_data.ApiModel.id,
                "name": version_data.ApiModel.name,
            },
            "endpoints": [
                {
                    "url": endpoint.endpoint,
                    "method": endpoint.method,
                    "description": endpoint.description,
                    "request_body": endpoint.request_body,
                    "response_body": endpoint.response_body,
                }
                for endpoint in endpoints
            ],
        }

    def get_full_api_version(
        self, api_id: int, version: str, supplier_id: str, role: str
    ):
        version_data = (
            db.session.query(ApiVersion, ApiModel)
            .filter(
                ApiVersion.api_id == api_id,
                ApiVersion.version == version,
                ApiModel.id == api_id,
            )
            .first()
        )

        if version_data is None:
            raise NotFoundError(
                "No API version found with id: {} and version: {}".format(
                    api_id, version
                )
            )

        if role == Role.SUPPLIER and version_data.ApiModel.supplier_id != supplier_id:
            raise BadRequestError("You are not authorized to view this version")

        endpoints = ApiVersionEndpoint.query.filter_by(
            api_id=api_id, version=version
        ).all()

        headers = ApiVersionHeader.query.filter_by(api_id=api_id, api_version=version)

        average_response_time = (
            db.session.query(func.avg(ApiRequest.response_time))
            .filter(ApiRequest.api_version == version)
            .filter(ApiRequest.api_id == api_id)
            .scalar()
        )

        return {
            "version": version_data.ApiVersion.version,
            "base_url": version_data.ApiVersion.base_url,
            "status": version_data.ApiVersion.status,
            "average_response_time": average_response_time,
            "created_at": version_data.ApiVersion.created_at.isoformat(),
            "updated_at": version_data.ApiVersion.updated_at.isoformat(),
            "api": {
                "id": version_data.ApiModel.id,
                "name": version_data.ApiModel.name,
            },
            "endpoints": [
                {
                    "url": endpoint.endpoint,
                    "method": endpoint.method,
                    "description": endpoint.description,
                    "request_body": endpoint.request_body,
                    "response_body": endpoint.response_body,
                }
                for endpoint in endpoints
            ],
            "headers": [
                {
                    "id": header.id,
                    "key": header.key,
                    "value": header.value,
                    "created_at": header.created_at.isoformat(),
                    "updated_at": header.updated_at.isoformat(),
                }
                for header in headers
            ],
        }

    def activate_version(self, api_id: int, version: str, supplier_id: int, role: str):
        api = ApiModel.query.filter_by(id=api_id).first()
        if api is None:
            raise NotFoundError("No API found with id: {}".format(api_id))

        api_version = ApiVersion.query.filter_by(api_id=api_id, version=version).first()

        if api_version is None:
            raise NotFoundError(
                "No API version found with id: {} and version: {}".format(
                    api_id, version
                )
            )

        if role == Role.SUPPLIER and api.supplier_id != supplier_id:
            raise BadRequestError("You are not authorized to activate this version")

        api_version.status = "active"
        db.session.commit()

    def deactivate_version(
        self, api_id: int, version: str, supplier_id: int, role: str
    ):
        api = ApiModel.query.filter_by(id=api_id).first()
        if api is None:
            raise NotFoundError("No API found with id: {}".format(api_id))

        api_version = ApiVersion.query.filter_by(api_id=api_id, version=version).first()

        if api_version is None:
            raise NotFoundError(
                "No API version found with id: {} and version: {}".format(
                    api_id, version
                )
            )

        if role == Role.SUPPLIER and api.supplier_id != supplier_id:
            raise BadRequestError("You are not authorized to disable this version")

        api_version.status = "disabled"
        db.session.commit()
