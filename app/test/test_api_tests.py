import pytest
from unittest.mock import Mock
from app.main.core.services.api_tests_service import ApiTestsService
from app.main.model.api_model import ApiModel

# from app.main.model.api_version_model import ApiVersion
from app.main.model.user_model import User
from app.main.model.api_category_model import ApiCategory
from app.main.model.api_header_model import ApiVersionHeader

from app.main.utils.roles import Role
from app.main.model.api_version_model import ApiVersion

# from app.main.model.api_request_model import ApiRequest
from app.main.utils.exceptions import BadRequestError

from app.main.utils.exceptions import NotFoundError
from faker import Faker


fake = Faker()


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
        name="API 1",
        description="API 1 Description",
        supplier_id=supplier.id,
        category_id=category.id,
        status="active",
    )

    test_db.session.add(api)
    test_db.session.commit()
    api_version = ApiVersion(
        api_id=api.id,
        version="1.0.0",
        base_url="https://example.com/api/v1",
        status="active",
    )
    test_db.session.add(api_version)
    test_db.session.commit()
    header1 = ApiVersionHeader(
        api_id=api.id,
        api_version=api_version.version,
        key="Authorization",
        value="Bearer token",
    )
    header2 = ApiVersionHeader(
        api_id=api.id,
        api_version=api_version.version,
        key="Content-Type",
        value="application/json",
    )
    test_db.session.add_all([header1, header2])
    test_db.session.commit()

    yield supplier, category, api, api_version, [header1, header2]

    objects_to_delete = [supplier, category, api, api_version, header1, header2]
    for obj in objects_to_delete:
        test_db.session.delete(obj)
    test_db.session.commit()


@pytest.fixture
def api_tests_service():

    mock_rest_client = Mock()
    mock_rest_client.get.return_value = ({"data": "mock_response"}, 200)
    mock_rest_client.post.return_value = ({"data": "mock_response"}, 201)
    mock_rest_client.patch.return_value = ({"data": "mock_response"}, 200)
    mock_rest_client.delete.return_value = ({"data": "mock_response"}, 204)
    return ApiTestsService(rest_client=mock_rest_client)


def test_get_success(mock_data, api_tests_service):
    api, api_version = (mock_data[2], mock_data[3])

    response, status = api_tests_service.test_get(api.id, api_version.version, "users")
    assert status == 200
    assert response == {"data": "mock_response"}


def test_get_api_not_found(mock_data, api_tests_service):
    api_version = mock_data[3]
    with pytest.raises(NotFoundError):
        api_tests_service.test_get(999, api_version.version, "users")


def test_get_api_inactive(mock_data, test_db, api_tests_service):
    api, api_version = (mock_data[2], mock_data[3])
    api.status = "inactive"
    test_db.session.commit()
    with pytest.raises(BadRequestError):
        api_tests_service.test_get(api.id, api_version.version, "users")


def test_get_version_not_found(mock_data, api_tests_service):
    api = mock_data[2]
    with pytest.raises(NotFoundError):
        api_tests_service.test_get(api.id, "2.0.0", "users")


def test_get_version_inactive(mock_data, test_db, api_tests_service):
    api, api_version = (mock_data[2], mock_data[3])
    api_version.status = "inactive"
    test_db.session.commit()
    with pytest.raises(BadRequestError):
        api_tests_service.test_get(api.id, api_version.version, "users")


def test_post_success(mock_data, api_tests_service):
    api, api_version = (mock_data[2], mock_data[3])
    data = {"name": "John Doe"}
    response, status = api_tests_service.test_post(
        api.id, api_version.version, "users", data
    )
    assert status == 201


def test_patch_success(mock_data, api_tests_service):
    api, api_version = (mock_data[2], mock_data[3])
    data = {"name": "Jane Doe"}
    response, status = api_tests_service.test_patch(
        api.id, api_version.version, "users/1", data
    )
    assert status == 200


def test_delete_success(mock_data, api_tests_service):
    api, api_version = (mock_data[2], mock_data[3])
    response, status = api_tests_service.test_delete(
        api.id, api_version.version, "users/1"
    )
    assert status == 204
