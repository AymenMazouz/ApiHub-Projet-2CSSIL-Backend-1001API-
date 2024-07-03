import pytest
from datetime import datetime, timedelta
from app.main.core.services.api_key_service import ApiKeyService
from app.main.model.api_model import ApiModel
from app.main.model.user_model import User
from app.main.model.api_subscription_model import ApiSubscription
from app.main.model.api_category_model import ApiCategory
from app.main.model.api_plan_model import ApiPlan
from app.main.model.api_key_model import ApiKey
from app.main.utils.roles import Role
from app.main.model.api_version_model import ApiVersion

# from app.main.model.api_request_model import ApiRequest
from app.main.utils.exceptions import BadRequestError
from app.main.utils.exceptions import NotFoundError
from faker import Faker


fake = Faker()
api_key_service = ApiKeyService()


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


def test_create_api_key_success(mock_data):
    supplier, subscription = (mock_data[0], mock_data[5])

    api_key_service.create_api_key(subscription.id, supplier.id)
    api_key = ApiKey.query.filter_by(subscription_id=subscription.id).all()
    assert len(api_key) == 2
    assert api_key[0].subscription_id == subscription.id


def test_create_api_key_subscription_not_found(mock_data):
    supplier = mock_data[0]
    subscription_id = 999

    with pytest.raises(NotFoundError, match=r"No subscription found with id: \d+"):
        api_key_service.create_api_key(subscription_id, supplier.id)


def test_create_api_key_no_requests_left(test_db, mock_data):
    supplier, api, subscription = (mock_data[0], mock_data[2], mock_data[5])
    subscription = ApiSubscription.query.filter_by(
        id=subscription.id, api_id=api.id
    ).first()
    subscription.max_requests = 0
    test_db.session.commit()

    with pytest.raises(
        BadRequestError,
        match="Subscription has no requests left, Please Renew Subscription",
    ):
        api_key_service.create_api_key(subscription.id, supplier.id)


def test_create_api_inactive_subscription(test_db, mock_data):
    supplier, api, subscription = (mock_data[0], mock_data[2], mock_data[5])
    subscription = ApiSubscription.query.filter_by(
        id=subscription.id, api_id=api.id
    ).first()
    subscription.status = "inactive"
    test_db.session.commit()

    with pytest.raises(BadRequestError, match="Subscription is not active"):
        api_key_service.create_api_key(subscription.id, supplier.id)


def test_create_api_expired_subscription(test_db, mock_data):
    supplier, api, subscription = (mock_data[0], mock_data[2], mock_data[5])
    subscription = ApiSubscription.query.filter_by(
        id=subscription.id, api_id=api.id
    ).first()
    subscription.end_date = datetime.now() - timedelta(days=1)
    test_db.session.commit()

    with pytest.raises(BadRequestError, match="Subscription has expired"):
        api_key_service.create_api_key(subscription.id, supplier.id)


def test_get_api_keys_success(mock_data):
    supplier, subscription, api_key = (
        mock_data[0],
        mock_data[5],
        mock_data[6],
    )
    expected_result = [
        {
            "key": api_key.key,
            "subscription_id": api_key.subscription_id,
            "status": api_key.status,
            "created_at": api_key.created_at.isoformat(),
        }
    ]
    result = api_key_service.get_api_keys(subscription.id, supplier.id)
    # Filter the result to include only the API key we created in the mock_data fixture
    filtered_result = [item for item in result if item["key"] == api_key.key]

    assert filtered_result == expected_result


def test_get_api_keys_subscription_not_found(mock_data):
    supplier = mock_data[0]

    subscription_id = 999

    with pytest.raises(
        NotFoundError,
        match=r"No subscription found with id: \d+",
    ):
        api_key_service.get_api_keys(subscription_id, supplier.id)


def test_deactivate_api_key_success(mock_data):
    supplier, api_key = (
        mock_data[0],
        mock_data[6],
    )

    api_key_service.deactivate_api_key(supplier.id, api_key.key)

    api_key = ApiKey.query.filter_by(key=api_key.key).first()
    assert api_key.status == "inactive"


def test_deactivate_api_key_not_found(mock_data):
    supplier = mock_data[0]

    api_key = "Invalide api key"
    with pytest.raises(
        NotFoundError,
        match=r"No api key found with key: .*",
    ):
        api_key_service.deactivate_api_key(supplier.id, api_key)


def test_deactivate_api_key_subscription_not_found(test_db, mock_data):
    supplier, api_key = (
        mock_data[0],
        mock_data[6],
    )
    api_key = ApiKey.query.filter_by(key=api_key.key).first()
    api_key.subscription_id = 999
    test_db.session.commit()
    with pytest.raises(NotFoundError, match="No subscription for this api key"):
        api_key_service.deactivate_api_key(supplier.id, api_key.key)


def test_deactivate_api_key_user_not_owner(test_db, mock_data):
    supplier, api, subscription, api_key = (
        mock_data[0],
        mock_data[2],
        mock_data[5],
        mock_data[6],
    )
    subscription = ApiSubscription.query.filter_by(
        id=subscription.id, api_id=api.id
    ).first()
    subscription.user_id = 999
    test_db.session.commit()
    with pytest.raises(BadRequestError, match="User does not own this api key"):
        api_key_service.deactivate_api_key(supplier.id, api_key.key)


def test_activate_api_key_success(test_db, mock_data):
    supplier, api_key = (
        mock_data[0],
        mock_data[6],
    )
    api_key = ApiKey.query.filter_by(key=api_key.key).first()
    api_key.status = "inactive"
    test_db.session.commit()

    api_key_service.activate_api_key(supplier.id, api_key.key)

    assert api_key.status == "active"


def test_activate_api_key_not_found(mock_data):
    supplier = mock_data[0]

    api_key = "Invalide api key"
    with pytest.raises(
        NotFoundError,
        match=r"No api key found with key: .*",
    ):
        api_key_service.activate_api_key(supplier.id, api_key)


def test_activate_api_key_subscription_not_found(test_db, mock_data):
    supplier, api_key = (
        mock_data[0],
        mock_data[6],
    )
    api_key = ApiKey.query.filter_by(key=api_key.key).first()
    api_key.subscription_id = 999
    test_db.session.commit()
    with pytest.raises(NotFoundError, match="No subscription for this api key"):
        api_key_service.activate_api_key(supplier.id, api_key.key)


def test_activate_api_key_user_not_owner(test_db, mock_data):
    supplier, api, subscription, api_key = (
        mock_data[0],
        mock_data[2],
        mock_data[5],
        mock_data[6],
    )
    subscription = ApiSubscription.query.filter_by(
        id=subscription.id, api_id=api.id
    ).first()
    subscription.user_id = 999
    test_db.session.commit()
    with pytest.raises(BadRequestError, match="User does not own this api key"):
        api_key_service.activate_api_key(supplier.id, api_key.key)
