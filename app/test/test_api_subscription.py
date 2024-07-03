import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
from app.main.model.api_model import ApiModel
from app.main.model.user_model import User
from app.main.model.api_version_model import ApiVersion
from app.main.model.api_subscription_model import ApiSubscription
from app.main.model.api_category_model import ApiCategory
from app.main.model.api_plan_model import ApiPlan

# from app.main.model.api_key_model import ApiKey
from app.main.utils.roles import Role
from app.main.core.services.api_subscription_service import ApiSubscriptionService
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
        chargily_price_id=1,
    )
    test_db.session.add_all([plan])
    test_db.session.commit()
    # subscription = ApiSubscription(
    #     api_id=api.id,
    #     plan_name=plan.name,
    #     user_id=supplier.id,
    #     start_date=datetime.now(),
    #     end_date=datetime.now() + timedelta(seconds=3600),
    #     max_requests=plan.max_requests,
    #     status="active",
    #     price=100,
    # )

    # test_db.session.add(subscription)
    # test_db.session.commit()
    # api_key = ApiKey(key="Api key", subscription_id=subscription.id)
    # test_db.session.add(api_key)
    # test_db.session.commit()

    yield supplier, category, api, plan, api_version
    # , subscription, api_key

    objects_to_delete = [
        supplier,
        category,
        api,
        plan,
        api_version,
        # subscription,
        # api_key,
    ]
    for obj in objects_to_delete:
        test_db.session.delete(obj)
    test_db.session.commit()


@pytest.fixture
def mock_chargily_api():
    mock_chargily_api = Mock()
    mock_chargily_api.create_checkout.return_value = "https://checkout.example.com"
    mock_chargily_api.verify_webhook_signature.return_value = True
    return mock_chargily_api


@pytest.fixture
def api_subscription_service(test_db, mock_chargily_api):
    return ApiSubscriptionService(chargily_api=mock_chargily_api)


# Tests for create_chargily_checkout
def test_create_chargily_checkout_success(mock_data, api_subscription_service):
    supplier, api, plan = (
        mock_data[0],
        mock_data[2],
        mock_data[3],
    )
    redirect_url = "https://example.com/redirect"
    result = api_subscription_service.create_charigly_checkout(
        api.id, plan.name, supplier.id, redirect_url
    )
    assert result == "https://checkout.example.com"


def test_create_chargily_checkout_api_not_found(mock_data, api_subscription_service):
    supplier, plan = (
        mock_data[0],
        mock_data[3],
    )
    api_id = 999
    redirect_url = "https://example.com/redirect"
    with pytest.raises(NotFoundError):
        api_subscription_service.create_charigly_checkout(
            api_id, plan.name, supplier.id, redirect_url
        )


def test_create_chargily_checkout_plan_not_found(mock_data, api_subscription_service):
    supplier, api = (
        mock_data[0],
        mock_data[2],
    )
    redirect_url = "https://example.com/redirect"
    with pytest.raises(NotFoundError):
        api_subscription_service.create_charigly_checkout(
            api.id, "invalid_plan_name", supplier.id, redirect_url
        )


def test_create_chargily_checkout_price_id_not_found(
    test_db, mock_data, api_subscription_service
):
    supplier, api, plan = (
        mock_data[0],
        mock_data[2],
        mock_data[3],
    )
    plan = ApiPlan.query.filter_by(api_id=api.id, name=plan.name).first()
    plan.chargily_price_id = None
    test_db.session.commit()
    redirect_url = "https://example.com/redirect"
    with pytest.raises(BadRequestError):
        api_subscription_service.create_charigly_checkout(
            api.id, plan.name, supplier.id, redirect_url
        )


def test_create_chargily_checkout_failed(
    mock_data, api_subscription_service, mock_chargily_api
):
    supplier, api, plan = (
        mock_data[0],
        mock_data[2],
        mock_data[3],
    )
    mock_chargily_api.create_checkout.return_value = None
    redirect_url = "https://example.com/redirect"
    with pytest.raises(BadRequestError):
        api_subscription_service.create_charigly_checkout(
            api.id, plan.name, supplier.id, redirect_url
        )


# Tests for handle_chargily_webhook
def test_handle_chargily_webhook_success(
    mock_data, api_subscription_service, monkeypatch
):
    supplier, api, plan = (
        mock_data[0],
        mock_data[2],
        mock_data[3],
    )
    request = Mock()
    request.json = {
        "type": "checkout.paid",
        "data": {
            "metadata": {
                "api_id": api.id,
                "plan_name": plan.name,
                "user_id": supplier.id,
            },
            "amount": plan.price,
        },
    }
    api_subscription_service.handle_chargily_webhook(request)
    subscription = ApiSubscription.query.filter_by(
        api_id=api.id, plan_name=plan.name, user_id=supplier.id
    ).first()
    assert subscription is not None


def test_handle_chargily_webhook_no_signature(mock_data, api_subscription_service):
    with pytest.raises(BadRequestError, match="No signature found in headers"):
        api_subscription_service.handle_chargily_webhook(Mock(headers={}))


def test_handle_chargily_webhook_no_body(mock_data, api_subscription_service):
    with pytest.raises(BadRequestError, match="No body found in request"):
        api_subscription_service.handle_chargily_webhook(Mock(data=None))


def test_handle_chargily_webhook_invalid_signature(
    mock_data, mock_chargily_api, api_subscription_service
):
    supplier, api, plan = (
        mock_data[0],
        mock_data[2],
        mock_data[3],
    )
    request = Mock()
    request.json = {
        "type": "checkout.paid",
        "data": {
            "metadata": {
                "api_id": api.id,
                "plan_name": plan.name,
                "user_id": supplier.id,
            },
            "amount": plan.price,
        },
    }
    request.headers = {"signature": "invalid_signature"}
    mock_chargily_api.verify_webhook_signature.return_value = False

    with pytest.raises(
        BadRequestError, match="Invalid signature, STOP TRYING TO HACK US"
    ):
        api_subscription_service.handle_chargily_webhook(request)


def test_handle_chargily_webhook_no_json(mock_data, api_subscription_service):
    request = Mock()
    request.headers = {"signature": "valid_signature"}
    request.json = None

    with pytest.raises(BadRequestError, match="No JSON found in request"):
        api_subscription_service.handle_chargily_webhook(request)


def test_handle_chargily_webhook_api_not_found(mock_data, api_subscription_service):
    supplier, plan = (
        mock_data[0],
        mock_data[3],
    )
    request = Mock()
    request.json = {
        "type": "checkout.paid",
        "data": {
            "metadata": {
                "api_id": 999,
                "plan_name": plan.name,
                "user_id": supplier.id,
            },
            "amount": plan.price,
        },
    }
    with pytest.raises(NotFoundError, match=r"No API found with id: \d+"):
        api_subscription_service.handle_chargily_webhook(request)


def test_handle_chargily_webhook_plan_not_found(mock_data, api_subscription_service):
    supplier, api, plan = (
        mock_data[0],
        mock_data[2],
        mock_data[3],
    )
    request = Mock()
    request.json = {
        "type": "checkout.paid",
        "data": {
            "metadata": {
                "api_id": api.id,
                "plan_name": "Invalide plan name",
                "user_id": supplier.id,
            },
            "amount": plan.price,
        },
    }
    with pytest.raises(NotFoundError, match=r"No plan found with name: .*"):
        api_subscription_service.handle_chargily_webhook(request)


# Tests for get_subscriptions
def test_get_subscriptions_success(test_db, mock_data, api_subscription_service):
    supplier, api, plan = (
        mock_data[0],
        mock_data[2],
        mock_data[3],
    )
    subscription = ApiSubscription(
        api_id=api.id,
        plan_name=plan.name,
        user_id=supplier.id,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        max_requests=plan.max_requests,
        status="active",
        price=plan.price,
    )
    test_db.session.add(subscription)
    test_db.session.commit()

    query_params = {
        "api_id": api.id,
        "plan_name": plan.name,
        "supplier_id": supplier.id,
    }
    result, meta = api_subscription_service.get_subscriptions(
        query_params, role=supplier.role
    )
    test_db.session.delete(subscription)
    test_db.session.commit()

    assert len(result) == 2
    assert result[1]["api_id"] == api.id
    assert result[1]["api_plan"] == plan.name
    assert result[1]["user_id"] == supplier.id


def test_get_subscriptions_supplier_role_missing_supplier_id(api_subscription_service):
    query_params = {}
    with pytest.raises(
        BadRequestError, match="Supplier ID is required for supplier role"
    ):
        api_subscription_service.get_subscriptions(query_params, role=Role.SUPPLIER)


def test_get_subscription_success(test_db, mock_data, api_subscription_service):
    supplier, api, plan = (
        mock_data[0],
        mock_data[2],
        mock_data[3],
    )
    subscription = ApiSubscription(
        api_id=api.id,
        plan_name=plan.name,
        user_id=supplier.id,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        max_requests=plan.max_requests,
        status="active",
        price=plan.price,
    )
    test_db.session.add(subscription)
    test_db.session.commit()

    result = api_subscription_service.get_subscription(
        subscription.id, supplier.id, role=Role.USER
    )
    assert result["id"] == subscription.id
    assert result["api_id"] == api.id
    assert result["user_id"] == supplier.id


def test_get_subscription_not_found(mock_data, api_subscription_service):
    supplier = mock_data[0]

    with pytest.raises(NotFoundError, match=r"No subscription found with id: \d+"):
        api_subscription_service.get_subscription(999, supplier.id, role=Role.USER)


def test_get_subscription_supplier_not_allowed(
    test_db, mock_data, api_subscription_service
):
    supplier, api, plan = (
        mock_data[0],
        mock_data[2],
        mock_data[3],
    )
    subscription = ApiSubscription(
        api_id=api.id,
        plan_name=plan.name,
        user_id=supplier.id,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        max_requests=plan.max_requests,
        status="active",
        price=plan.price,
    )
    test_db.session.add(subscription)
    test_db.session.commit()

    with pytest.raises(
        BadRequestError, match="You are not allowed to view this subscription"
    ):
        api_subscription_service.get_subscription(
            subscription.id, "another_supplier_id", role=Role.SUPPLIER
        )


def test_get_subscription_user_not_allowed(
    test_db, mock_data, api_subscription_service
):
    user, api, plan = (
        mock_data[0],
        mock_data[2],
        mock_data[3],
    )
    subscription = ApiSubscription(
        api_id=api.id,
        plan_name=plan.name,
        user_id=user.id,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        max_requests=plan.max_requests,
        status="active",
        price=plan.price,
    )
    test_db.session.add(subscription)
    test_db.session.commit()

    with pytest.raises(
        BadRequestError, match="You are not allowed to view this subscription"
    ):
        api_subscription_service.get_subscription(
            subscription.id, "another_user_id", role=Role.USER
        )
