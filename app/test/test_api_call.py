import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
from app.main.core.services.api_call_service import ApiCallService
from app.main.model.api_model import ApiModel

# from app.main.model.api_version_model import ApiVersion
from app.main.model.user_model import User
from app.main.model.api_subscription_model import ApiSubscription
from app.main.model.api_category_model import ApiCategory
from app.main.model.api_plan_model import ApiPlan
from app.main.model.api_key_model import ApiKey
from app.main.utils.roles import Role
from app.main.model.api_version_model import ApiVersion
from app.main.model.api_request_model import ApiRequest
from app.main.utils.exceptions import BadRequestError

# , NotFoundError
from faker import Faker


fake = Faker()


@pytest.fixture
def api_call_service():

    mock_rest_client = Mock()
    mock_rest_client.get.return_value = ({"data": "mock_response"}, 200)
    return ApiCallService(rest_client=mock_rest_client)


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
        version="3.0.0",
        base_url="https://example.com/api/v1",
        status="active",
    )
    test_db.session.add(api_version)
    test_db.session.commit()

    plan = ApiPlan(
        name="Basic Plan",
        description="Basic plan description",
        price=10,
        max_requests=1000,
        duration=30,
        api_id=api.id,
    )
    test_db.session.add_all([plan])
    test_db.session.commit()
    subscription = ApiSubscription(
        api_id=api.id,
        plan_name=plan.name,
        user_id=supplier.id,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(seconds=3600),
        max_requests=plan.max_requests,
        status="active",
        price=100,
    )

    test_db.session.add(subscription)
    test_db.session.commit()
    api_key = ApiKey(key="Api key", subscription_id=subscription.id)
    test_db.session.add(api_key)
    test_db.session.commit()

    yield supplier, category, api, plan, api_version, subscription, api_key

    objects_to_delete = [
        supplier,
        category,
        api,
        plan,
        api_version,
        subscription,
        api_key,
    ]
    for obj in objects_to_delete:
        test_db.session.delete(obj)
    test_db.session.commit()


def test_call_get_valid(api_call_service, mock_data):
    api, api_version, api_key = (
        mock_data[2],
        mock_data[4],
        mock_data[6],
    )

    response, status = api_call_service.call_get(
        api.id, api_version.version, "test_params", api_key.key
    )

    assert status == 200
    assert response == {"data": "mock_response"}
    new_request = ApiRequest.query.filter_by(api_id=api.id).first()
    assert new_request is not None


def test_call_get_invalid_api_key(api_call_service, mock_data):
    api, api_version = (
        mock_data[2],
        mock_data[4],
    )
    with pytest.raises(BadRequestError, match="Invalid API key"):
        api_call_service.call_get(
            api.id, api_version.version, "test_params", "invalid_key"
        )


def test_call_get_inactive_api_key(test_db, api_call_service, mock_data):
    api, api_version, api_key = (
        mock_data[2],
        mock_data[4],
        mock_data[6],
    )
    api_key_data = ApiKey.query.filter_by(key=api_key.key).first()
    api_key_data.status = "inactive"

    test_db.session.commit()

    with pytest.raises(BadRequestError, match="API key is not active"):
        api_call_service.call_get(
            api.id, api_version.version, "test_params", api_key_data.key
        )


def test_call_get_invalid_subscription(test_db, api_call_service, mock_data):
    api, api_version, api_key = (
        mock_data[2],
        mock_data[4],
        mock_data[6],
    )
    api_key_data = ApiKey.query.filter_by(key=api_key.key).first()
    api_key_data.subscription_id = 999

    test_db.session.commit()

    with pytest.raises(BadRequestError, match="Invalid subscription"):
        api_call_service.call_get(
            api.id, api_version.version, "test_params", api_key_data.key
        )


def test_call_get_inactive_subscription(test_db, api_call_service, mock_data):
    api, api_version, subscription, api_key = (
        mock_data[2],
        mock_data[4],
        mock_data[5],
        mock_data[6],
    )
    subscription = ApiSubscription.query.filter_by(
        id=subscription.id, api_id=api.id
    ).first()
    subscription.status = "inactive"
    test_db.session.commit()

    with pytest.raises(BadRequestError, match="Subscription is not active"):
        api_call_service.call_get(
            api.id, api_version.version, "test_params", api_key.key
        )


def test_call_get_expired_subscription(test_db, api_call_service, mock_data):
    api, api_version, subscription, api_key = (
        mock_data[2],
        mock_data[4],
        mock_data[5],
        mock_data[6],
    )
    subscription = ApiSubscription.query.filter_by(
        id=subscription.id, api_id=api.id
    ).first()
    subscription.end_date = datetime.now() - timedelta(days=1)
    test_db.session.commit()

    with pytest.raises(BadRequestError, match="Subscription has expired"):
        api_call_service.call_get(
            api.id, api_version.version, "test_params", api_key.key
        )


def test_call_get_no_requests_left(test_db, api_call_service, mock_data):
    api, api_version, subscription, api_key = (
        mock_data[2],
        mock_data[4],
        mock_data[5],
        mock_data[6],
    )
    subscription = ApiSubscription.query.filter_by(
        id=subscription.id, api_id=api.id
    ).first()
    subscription.max_requests = 0
    test_db.session.commit()

    with pytest.raises(BadRequestError, match="Subscription has no requests left"):
        api_call_service.call_get(
            api.id, api_version.version, "test_params", api_key.key
        )
