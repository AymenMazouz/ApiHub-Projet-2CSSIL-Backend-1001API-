import pytest

from app.main.utils.exceptions import NotFoundError, BadRequestError
from app.main.model.api_category_model import ApiCategory
from app.main.model.api_model import ApiModel
from app.main.model.api_request_model import ApiRequest
from app.main.model.user_model import User
from app.main.model.api_version_model import ApiVersion
from app.main.model.api_version_endpoint_model import ApiVersionEndpoint
from app.main.model.api_header_model import ApiVersionHeader
from app.main.utils.roles import Role
from app.main.core.services.api_version_service import ApiVersionService
from faker import Faker
from sqlalchemy import func


fake = Faker()
api_version_service = ApiVersionService()


@pytest.fixture
def mock_data(test_db):
    password = fake.password()
    supplier = User(
        email="supplier@gmail.com",
        firstname="supplier",
        lastname="supplier",
        password=password,
        role=Role.SUPPLIER,
    )
    category = ApiCategory(
        name="Test category", description="Test category Description", created_by=1
    )

    test_db.session.add_all([supplier, category])
    test_db.session.commit()
    api = ApiModel(
        name="API",
        description="API Description",
        supplier_id=supplier.id,
        category_id=category.id,
        status="active",
    )
    test_db.session.add(api)
    test_db.session.commit()

    api_version1 = ApiVersion(
        api_id=api.id,
        version="3.0.0",
        base_url="https://example.com/api/v1",
        status="active",
    )
    api_version2 = ApiVersion(
        api_id=api.id,
        version="4.0.0",
        base_url="https://example.com/api/v2",
        status="inactive",
    )
    test_db.session.add_all([api_version1, api_version2])
    test_db.session.commit()
    endpoint1 = ApiVersionEndpoint(
        api_id=api.id,
        version=api_version1.version,
        endpoint="/users",
        method="GET",
        description="Get users",
        request_body="",
        response_body="",
    )
    endpoint2 = ApiVersionEndpoint(
        api_id=api.id,
        version=api_version1.version,
        endpoint="/users/{id}",
        method="GET",
        description="Get a user",
        request_body="",
        response_body="",
    )
    test_db.session.add_all([endpoint1, endpoint2])
    test_db.session.commit()
    header1 = ApiVersionHeader(
        api_id=api.id,
        api_version=api_version1.version,
        key="Authorization",
        value="Bearer token",
    )
    test_db.session.add(header1)
    test_db.session.commit()
    password = fake.password()
    another_user = User(
        firstname="Jane",
        lastname="Doe",
        email="jane@example.com",
        role=Role.SUPPLIER,
        password=password,
    )
    test_db.session.add(another_user)
    test_db.session.commit()
    yield supplier, category, api, [api_version1, api_version2], [
        endpoint1,
        endpoint2,
    ], [header1], another_user

    objects_to_delete = [
        supplier,
        category,
        api,
        api_version1,
        api_version2,
        endpoint1,
        endpoint2,
        header1,
        another_user,
    ]
    for obj in objects_to_delete:
        test_db.session.delete(obj)
    test_db.session.commit()


def test_get_api_versions(mock_data):
    api, versions = (
        mock_data[2],
        mock_data[3],
    )
    expected_result = [
        {
            "version": version.version,
            "status": version.status,
            "created_at": version.created_at.isoformat(),
            "updated_at": version.updated_at.isoformat(),
        }
        for version in versions
    ]

    result = api_version_service.get_api_versions(api.id, {})
    assert result == expected_result


def test_get_api_versions_with_status_filter(mock_data):
    api, versions = (
        mock_data[2],
        mock_data[3],
    )
    expected_result = [
        {
            "version": versions[0].version,
            "status": versions[0].status,
            "created_at": versions[0].created_at.isoformat(),
            "updated_at": versions[0].updated_at.isoformat(),
        }
    ]

    result = api_version_service.get_api_versions(api.id, {"status": "active"})
    assert result == expected_result


def test_create_api_version_valid(mock_data):
    supplier, api = (
        mock_data[0],
        mock_data[2],
    )
    data = {
        "version": "1.0.0",
        "base_url": "https://example.com/api/v1",
        "endpoints": [
            {
                "url": "/users",
                "method": "GET",
                "description": "Get a list of users",
                "request_body": "",
                "response_body": '"users":"id": 1, "name": "John Doe"',
            }
        ],
        "headers": [{"key": "Authorization", "value": "Bearer token"}],
    }

    api_version_service.create_api_version(api.id, supplier.id, data)

    version = ApiVersion.query.filter_by(api_id=api.id, version=data["version"]).first()
    assert version is not None
    assert version.base_url == data["base_url"]
    assert version.status == "active"


def test_create_api_version_not_found(mock_data):
    supplier = mock_data[0]
    data = {"version": "1.0.0", "base_url": "https://example.com/api/v1"}

    with pytest.raises(NotFoundError, match=r"No API found with id: \d+"):
        api_version_service.create_api_version(999, supplier.id, data)


def test_create_api_version_already_exists(test_db, mock_data):
    supplier, api = (
        mock_data[0],
        mock_data[2],
    )
    data = {"version": "2.0.0", "base_url": "https://example.com/api/v1"}
    api_version = ApiVersion(
        api_id=api.id,
        version=data["version"],
        base_url=data["base_url"],
        status="active",
    )
    test_db.session.add(api_version)
    test_db.session.commit()

    with pytest.raises(BadRequestError, match=r"API version already exists"):
        api_version_service.create_api_version(api.id, supplier.id, data)


def test_get_api_version(test_db, mock_data):
    api, versions, endpoints = (mock_data[2], mock_data[3], mock_data[4])
    api_version = versions[0]
    average_response_time = (
        test_db.session.query(func.avg(ApiRequest.response_time))
        .filter(ApiRequest.api_id == api.id)
        .filter(ApiRequest.api_id == api.id)
        .scalar()
    )
    expected_result = {
        "version": api_version.version,
        "status": api_version.status,
        "average_response_time": average_response_time,
        "created_at": api_version.created_at.isoformat(),
        "updated_at": api_version.updated_at.isoformat(),
        "api": {"id": api.id, "name": api.name},
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

    result = api_version_service.get_api_version(api.id, api_version.version)
    assert result == expected_result


def test_get_api_version_not_found(mock_data):
    api = mock_data[2]

    with pytest.raises(
        NotFoundError,
        match=r"No API version found with id: \d+ and version: \d+\.\d+\.\d+",
    ):
        api_version_service.get_api_version(api.id, "10.0.0")


def test_get_full_api_version(test_db, mock_data):
    supplier, api, versions, endpoints, headers = (
        mock_data[0],
        mock_data[2],
        mock_data[3],
        mock_data[4],
        mock_data[5],
    )
    api_version = versions[0]
    average_response_time = (
        test_db.session.query(func.avg(ApiRequest.response_time))
        .filter(ApiRequest.api_version == api_version.version)
        .filter(ApiRequest.api_id == api.id)
        .scalar()
    )
    expected_result = {
        "version": api_version.version,
        "base_url": api_version.base_url,
        "status": api_version.status,
        "average_response_time": average_response_time,
        "created_at": api_version.created_at.isoformat(),
        "updated_at": api_version.updated_at.isoformat(),
        "api": {"id": api.id, "name": api.name},
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

    result = api_version_service.get_full_api_version(
        api.id, api_version.version, supplier.id, supplier.role
    )
    assert result == expected_result


def test_get_full_api_version_not_found(mock_data):
    supplier, api = (
        mock_data[0],
        mock_data[2],
    )

    with pytest.raises(
        NotFoundError,
        match=r"No API version found with id: \d+ and version: \d+\.\d+\.\d+",
    ):
        api_version_service.get_full_api_version(
            api.id, "10.0.0", supplier.id, supplier.role
        )


def test_get_full_api_version_not_authorized(test_db, mock_data):
    api, versions, another_user = (
        mock_data[2],
        mock_data[3],
        mock_data[6],
    )
    api_version = versions[0]

    with pytest.raises(
        BadRequestError, match=r"You are not authorized to view this version"
    ):
        api_version_service.get_full_api_version(
            api.id, api_version.version, another_user.id, another_user.role
        )


def test_activate_version_valid(mock_data):
    user, api, versions = (
        mock_data[0],
        mock_data[2],
        mock_data[3],
    )
    api_version = versions[0]

    api_version_service.activate_version(
        api.id, api_version.version, user.id, user.role
    )

    api_version = ApiVersion.query.filter_by(
        api_id=api.id, version=api_version.version
    ).first()
    assert api_version.status == "active"


def test_activate_version_not_found_api(mock_data):
    supplier, versions = (
        mock_data[0],
        mock_data[3],
    )
    api_version = versions[0]

    with pytest.raises(NotFoundError, match=r"No API found with id: \d+"):
        api_version_service.activate_version(
            999, api_version.version, supplier.id, supplier.role
        )


def test_activate_version_not_found_version(mock_data):
    supplier, api = (
        mock_data[0],
        mock_data[2],
    )

    with pytest.raises(
        NotFoundError,
        match=r"No API version found with id: \d+ and version: \d+\.\d+\.\d+",
    ):
        api_version_service.activate_version(
            api.id, "10.0.0", supplier.id, supplier.role
        )


def test_activate_version_not_authorized(test_db, mock_data):
    api, versions, another_user = (
        mock_data[2],
        mock_data[3],
        mock_data[6],
    )
    api_version = versions[0]

    with pytest.raises(
        BadRequestError, match=r"You are not authorized to activate this version"
    ):
        api_version_service.activate_version(
            api.id, api_version.version, another_user.id, another_user.role
        )


def test_deactivate_version_valid(mock_data):
    user, api, versions = (
        mock_data[0],
        mock_data[2],
        mock_data[3],
    )
    api_version = versions[0]

    api_version_service.deactivate_version(
        api.id, api_version.version, user.id, user.role
    )

    api_version = ApiVersion.query.filter_by(
        api_id=api.id, version=api_version.version
    ).first()
    assert api_version.status == "disabled"


def test_deactivate_version_not_found_api(mock_data):
    supplier, versions = (
        mock_data[0],
        mock_data[3],
    )
    api_version = versions[0]

    with pytest.raises(NotFoundError, match=r"No API found with id: \d+"):
        api_version_service.deactivate_version(
            999, api_version.version, supplier.id, supplier.role
        )


def test_deactivate_version_not_found_version(mock_data):
    supplier, api = (
        mock_data[0],
        mock_data[2],
    )

    with pytest.raises(
        NotFoundError,
        match=r"No API version found with id: \d+ and version: \d+\.\d+\.\d+",
    ):
        api_version_service.deactivate_version(
            api.id, "10.0.0", supplier.id, supplier.role
        )


def test_deactivate_version_not_authorized(test_db, mock_data):
    api, versions, another_user = (
        mock_data[2],
        mock_data[3],
        mock_data[6],
    )
    api_version = versions[0]

    with pytest.raises(
        BadRequestError, match=r"You are not authorized to disable this version"
    ):
        api_version_service.deactivate_version(
            api.id, api_version.version, another_user.id, another_user.role
        )
