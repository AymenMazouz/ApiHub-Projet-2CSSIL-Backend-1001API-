import pytest
from unittest.mock import Mock
from app.main.model.api_category_model import ApiCategory
from app.main.model.api_model import ApiModel
from app.main.model.api_request_model import ApiRequest
from app.main.model.user_model import User
from app.main.model.api_plan_model import ApiPlan
from sqlalchemy import func


# from .fixtures.user.add_user import add_user
from faker import Faker
from app.main.utils.roles import Role
from app.main.core.services.api_service import ApiService
from app.main.core.lib.impl.media_manager_impl import MediaManagerImpl
from app.main.utils.exceptions import BadRequestError


from app.main.utils.exceptions import NotFoundError

fake = Faker()


@pytest.fixture(scope="module")
def api_service(test_db):
    mock_chargily_api = Mock()
    mock_chargily_api.create_product.return_value = "product_id"
    mock_chargily_api.create_price.side_effect = ["price_id_1", "price_id_2"]

    mock_media_manager = Mock(spec=MediaManagerImpl)
    mock_media_manager.get_media_url_by_id.side_effect = (
        lambda media_id: f"https://example.com/media_{media_id}.jpg"
    )

    return ApiService(media_manager=mock_media_manager, chargily_api=mock_chargily_api)


@pytest.fixture
def mock_data(test_db):
    password1 = fake.password()
    supplier1 = User(
        email="supplier1@gmail.com",
        firstname="supplier1",
        lastname="supplier1",
        password=password1,
        role=Role.SUPPLIER,
    )
    password2 = fake.password()
    supplier2 = User(
        email="supplier2@gmail.com",
        firstname="supplier2",
        lastname="supplier2",
        password=password2,
        role=Role.SUPPLIER,
    )
    category1 = ApiCategory(
        name="Test category1", description="Test category1 Description", created_by=1
    )
    category2 = ApiCategory(
        name="Test category2", description="Test category2 Description", created_by=1
    )
    category3 = ApiCategory(
        name="Test category3", description="Test category3 Description", created_by=1
    )
    test_db.session.add_all([supplier1, supplier2, category1, category2, category3])
    test_db.session.commit()

    api1 = ApiModel(
        name="API 1",
        description="API 1 Description",
        supplier_id=supplier1.id,
        category_id=category1.id,
        status="active",
    )
    api2 = ApiModel(
        name="API 2",
        description="API 2 Description",
        supplier_id=supplier2.id,
        category_id=category2.id,
        status="inactive",
    )
    api3 = ApiModel(
        name="API 3",
        description="API 3 Description",
        supplier_id=supplier1.id,
        category_id=category3.id,
        status="active",
    )
    test_db.session.add_all([api1, api2, api3])
    test_db.session.commit()

    plan1 = ApiPlan(
        name="Basic Plan",
        description="Basic plan description",
        price=10,
        max_requests=1000,
        duration=30,
        api_id=api1.id,
    )
    plan2 = ApiPlan(
        name="Premium Plan",
        description="Premium plan description",
        price=20,
        max_requests=5000,
        duration=90,
        api_id=api1.id,
    )
    test_db.session.add_all([plan1, plan2])
    test_db.session.commit()
    plans = [plan1, plan2]

    yield supplier1, supplier2, category1, category2, category3, api1, api2, api3, plans

    objects_to_delete = [
        supplier1,
        supplier2,
        category1,
        category2,
        category3,
        api1,
        api2,
        api3,
        plan1,
        plan2,
    ]
    for obj in objects_to_delete:
        test_db.session.delete(obj)
    test_db.session.commit()


def test_get_apis_default(api_service, mock_data):
    supplier1, supplier2, category1, category2, category3, api1, api2, api3, *_ = (
        mock_data
    )
    expected_result = [
        {
            "id": api1.id,
            "name": api1.name,
            "description": api1.description,
            "category_id": api1.category_id,
            "category": {"id": category1.id, "name": category1.name},
            "supplier_id": api1.supplier_id,
            "supplier": {
                "id": supplier1.id,
                "firstname": supplier1.firstname,
                "lastname": supplier1.lastname,
            },  # Update supplier details
            "status": api1.status,
            "created_at": api1.created_at.isoformat(),
            "updated_at": api1.updated_at.isoformat(),
            "image": f"https://example.com/media_{api1.id}.jpg",
        },
        {
            "id": api2.id,
            "name": api2.name,
            "description": api2.description,
            "category_id": api2.category_id,
            "category": {"id": category2.id, "name": category2.name},
            "supplier_id": api2.supplier_id,
            "supplier": {
                "id": supplier2.id,
                "firstname": supplier2.firstname,
                "lastname": supplier2.lastname,
            },
            "status": api2.status,
            "created_at": api2.created_at.isoformat(),
            "updated_at": api2.updated_at.isoformat(),
            "image": f"https://example.com/media_{api2.id}.jpg",
        },
        {
            "id": api3.id,
            "name": api3.name,
            "description": api3.description,
            "category_id": api3.category_id,
            "category": {
                "id": category3.id,
                "name": category3.name,
            },  # Update category details
            "supplier_id": api3.supplier_id,
            "supplier": {
                "id": supplier1.id,
                "firstname": supplier1.firstname,
                "lastname": supplier1.lastname,
            },
            "status": api3.status,
            "created_at": api3.created_at.isoformat(),
            "updated_at": api3.updated_at.isoformat(),
            "image": f"https://example.com/media_{api3.id}.jpg",
        },
    ]
    expected_pagination = {
        "total": 3,
        "page": 1,
        "per_page": 10,
        "pages": 1,
    }  # Update total and pages

    result, pagination = api_service.get_apis({})

    assert result == expected_result
    assert pagination == expected_pagination


def test_create_api(api_service, mock_data):
    category = mock_data[2]
    category_id = category.id
    data = {
        "name": "Test API",
        "description": "This is a test API",
        "category_id": category_id,
        "plans": [
            {
                "name": "Basic Plan",
                "price": 10,
                "description": "Basic plan description",
                "max_requests": 1000,
                "duration": 30,
            },
            {
                "name": "Premium Plan",
                "price": 20,
                "description": "Premium plan description",
                "max_requests": 5000,
                "duration": 90,
            },
        ],
    }
    user_id = 1

    # Act
    api_service.create_api(data, user_id)

    # Assert
    api_service.chargily_api.create_product.assert_called_once_with(
        data["name"], data["description"]
    )
    assert api_service.chargily_api.create_price.call_count == 2
    api_service.chargily_api.create_price.assert_any_call(
        "product_id", data["plans"][0]["price"]
    )
    api_service.chargily_api.create_price.assert_any_call(
        "product_id", data["plans"][1]["price"]
    )


def test_create_api_category_not_found(api_service):
    data = {
        "name": "Test API",
        "description": "This is a test API",
        "category_id": 999,  # Non-existent category ID
        "plans": [],
    }
    user_id = 1

    # Act & Assert
    with pytest.raises(NotFoundError):
        api_service.create_api(data, user_id)


def test_create_api_duplicate_plan_names(api_service, mock_data):
    category = mock_data[2]
    category_id = category.id
    data = {
        "name": "Test API",
        "description": "This is a test API",
        "category_id": category_id,
        "plans": [
            {
                "name": "Basic Plan",
                "price": 10,
                "description": "Basic plan description",
                "max_requests": 1000,
                "duration": 30,
            },
            {
                "name": "Basic Plan",  # Duplicate plan name
                "price": 20,
                "description": "Premium plan description",
                "max_requests": 5000,
                "duration": 90,
            },
        ],
    }
    user_id = 1

    # Act & Assert
    with pytest.raises(BadRequestError):
        api_service.create_api(data, user_id)


def test_create_api_negative_plan_price(api_service, mock_data):
    category = mock_data[2]
    category_id = category.id
    data = {
        "name": "Test API",
        "description": "This is a test API",
        "category_id": category_id,
        "plans": [
            {
                "name": "Basic Plan",
                "price": -10,  # Negative price
                "description": "Basic plan description",
                "max_requests": 1000,
                "duration": 30,
            },
        ],
    }
    user_id = 1

    # Act & Assert
    with pytest.raises(BadRequestError, match=r"Price cannot be negative"):
        api_service.create_api(data, user_id)


def test_create_api_negative_max_requests(api_service, mock_data):
    category = mock_data[2]
    category_id = category.id
    data = {
        "name": "Test API",
        "description": "This is a test API",
        "category_id": category_id,
        "plans": [
            {
                "name": "Basic Plan",
                "price": 10,
                "description": "Basic plan description",
                "max_requests": -1000,  # Negative max_requests
                "duration": 30,
            },
        ],
    }
    user_id = 1

    # Act & Assert
    with pytest.raises(BadRequestError, match=r"Max requests cannot be negative"):
        api_service.create_api(data, user_id)


def test_create_api_negative_duration(api_service, mock_data):
    category = mock_data[2]
    category_id = category.id
    data = {
        "name": "Test API",
        "description": "This is a test API",
        "category_id": category_id,
        "plans": [
            {
                "name": "Basic Plan",
                "price": 10,
                "description": "Basic plan description",
                "max_requests": 1000,
                "duration": -30,  # Negative duration
            },
        ],
    }
    user_id = 1

    # Act & Assert
    with pytest.raises(BadRequestError, match=r"Duration cannot be negative"):
        api_service.create_api(data, user_id)


def test_create_api_chargily_product_creation_failed(
    api_service, mock_data, monkeypatch
):
    category = mock_data[2]
    category_id = category.id
    data = {
        "name": "Test API",
        "description": "This is a test API",
        "category_id": category_id,
        "plans": [],
    }
    user_id = 1

    # Mock the chargily_api.create_product method to return None
    monkeypatch.setattr(api_service.chargily_api, "create_product", lambda *args: None)

    # Act & Assert
    with pytest.raises(
        BadRequestError, match=r"Failed to create product in chargily API"
    ):
        api_service.create_api(data, user_id)


def test_create_api_chargily_price_creation_failed(api_service, mock_data, monkeypatch):
    category = mock_data[2]
    category_id = category.id
    data = {
        "name": "Test API",
        "description": "This is a test API",
        "category_id": category_id,
        "plans": [
            {
                "name": "Basic Plan",
                "price": 10,
                "description": "Basic plan description",
                "max_requests": 1000,
                "duration": 30,
            },
        ],
    }
    user_id = 1

    # Mock the chargily_api.create_price method to return None
    monkeypatch.setattr(api_service.chargily_api, "create_price", lambda *args: None)

    # Act & Assert
    with pytest.raises(
        BadRequestError, match=r"Failed to create price in chargily API"
    ):
        api_service.create_api(data, user_id)


def test_get_apis_with_filter(api_service, mock_data):
    supplier1, _, category1, _, _, api1, *_ = mock_data
    query_params = {
        "status": "active",
        "categoryIds": str(category1.id),
        "supplierId": str(supplier1.id),
    }
    expected_result = [
        {
            "id": api1.id,
            "name": api1.name,
            "description": api1.description,
            "category_id": api1.category_id,
            "category": {"id": category1.id, "name": category1.name},
            "supplier_id": api1.supplier_id,
            "supplier": {
                "id": supplier1.id,
                "firstname": supplier1.firstname,
                "lastname": supplier1.lastname,
            },
            "status": api1.status,
            "created_at": api1.created_at.isoformat(),
            "updated_at": api1.updated_at.isoformat(),
            "image": f"https://example.com/media_{api1.id}.jpg",
        }
    ]
    expected_pagination = {"total": 1, "page": 1, "per_page": 10, "pages": 1}

    result, pagination = api_service.get_apis(query_params)

    assert result == expected_result
    assert pagination == expected_pagination


def test_get_api_by_id(test_db, api_service, mock_data):
    supplier1, category1, api1, plans = (
        mock_data[0],
        mock_data[2],
        mock_data[5],
        mock_data[8],
    )
    average_response_time = (
        test_db.session.query(func.avg(ApiRequest.response_time))
        .filter(ApiRequest.api_id == api1.id)
        .scalar()
    )
    expected_result = {
        "id": api1.id,
        "name": api1.name,
        "description": api1.description,
        "status": api1.status,
        "average_response_time": average_response_time,
        "category_id": api1.category_id,
        "category": {"id": category1.id, "name": category1.name},
        "supplier_id": api1.supplier_id,
        "supplier": {
            "id": supplier1.id,
            "firstname": supplier1.firstname,
            "lastname": supplier1.lastname,
        },
        "created_at": api1.created_at.isoformat(),
        "updated_at": api1.updated_at.isoformat(),
        "image": f"https://example.com/media_{api1.id}.jpg",
        "plans": [
            {
                "name": plan.name,
                "description": plan.description,
                "price": plan.price,
                "max_requests": plan.max_requests,
                "duration": plan.duration,
            }
            for plan in plans
        ],
    }

    result = api_service.get_api_by_id(api1.id)

    assert result == expected_result


def test_get_api_by_id_not_found(api_service):
    with pytest.raises(NotFoundError, match=r"No API found with id: \d+"):
        api_service.get_api_by_id(999)


def test_update_api_valid(api_service, mock_data):
    supplier1, category2, api1 = (
        mock_data[0],
        mock_data[3],
        mock_data[5],
    )
    data = {
        "name": "Updated API 1",
        "description": "Updated API 1 Description",
        "category_id": category2.id,
    }

    api_service.update_api(api1.id, supplier1.id, data)

    api1 = ApiModel.query.get(api1.id)
    assert api1.name == data["name"]
    assert api1.description == data["description"]
    assert api1.category_id == data["category_id"]


def test_update_api_not_found(api_service, mock_data):
    supplier1 = mock_data[0]
    data = {"name": "Updated API"}

    with pytest.raises(NotFoundError, match=r"No API found with id: \d+"):
        api_service.update_api(999, supplier1.id, data)


def test_update_api_not_owner(api_service, mock_data):
    supplier2, api1 = (
        mock_data[1],
        mock_data[5],
    )
    data = {"name": "Updated API"}

    with pytest.raises(BadRequestError, match=r"You are not the owner of the API"):
        api_service.update_api(api1.id, supplier2.id, data)


def test_update_api_category_not_found(api_service, mock_data):
    supplier1, api1 = (
        mock_data[0],
        mock_data[5],
    )
    data = {"category_id": 999}

    with pytest.raises(NotFoundError, match=r"No API Category found with id: \d+"):
        api_service.update_api(api1.id, supplier1.id, data)


def test_activate_api_valid(api_service, mock_data):
    supplier1, api1 = (
        mock_data[0],
        mock_data[5],
    )

    api_service.activate_api(api1.id, supplier1.id, Role.SUPPLIER)

    api1 = ApiModel.query.get(api1.id)
    assert api1.status == "active"


def test_activate_api_not_found(api_service, mock_data):
    supplier1 = mock_data[0]

    with pytest.raises(NotFoundError, match=r"No API found with id: \d+"):
        api_service.activate_api(999, supplier1.id, Role.SUPPLIER)


def test_activate_api_not_owner(api_service, mock_data):
    supplier2, api1 = (
        mock_data[1],
        mock_data[5],
    )

    with pytest.raises(BadRequestError, match=r"You are not the owner of the API"):
        api_service.activate_api(api1.id, supplier2.id, Role.SUPPLIER)


def test_deactivate_api_valid(api_service, mock_data):
    supplier1, api1 = (
        mock_data[0],
        mock_data[5],
    )

    api_service.deactivate_api(api1.id, supplier1.id, Role.SUPPLIER)

    api1 = ApiModel.query.get(api1.id)
    assert api1.status == "inactive"


def test_deactivate_api_not_found(api_service, mock_data):
    supplier1 = mock_data[0]

    with pytest.raises(NotFoundError, match=r"No API found with id: \d+"):
        api_service.deactivate_api(999, supplier1.id, Role.SUPPLIER)


def test_deactivate_api_not_owner(api_service, mock_data):
    supplier2, api1 = (
        mock_data[1],
        mock_data[5],
    )

    with pytest.raises(BadRequestError, match=r"You are not the owner of the API"):
        api_service.deactivate_api(api1.id, supplier2.id, Role.SUPPLIER)
