import pytest
from app.main.core.services.api_tickets_service import ApiTicketsService
from app.main.utils.exceptions import NotFoundError, BadRequestError
from app.main.model.api_category_model import ApiCategory
from app.main.model.api_model import ApiModel
from app.main.model.user_model import User
from app.main.model.api_plan_model import ApiPlan
from faker import Faker
from app.main.utils.roles import Role

fake = Faker()


@pytest.fixture(scope="module")
def api_ticket_service(test_db):

    return ApiTicketsService()


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


def test_create_ticket(api_ticket_service, mock_data):
    new_ticket = api_ticket_service.create_ticket(
        api_id=mock_data[5].id,
        ticket={
            "subject": "New Ticket",
            "description": "New Ticket description",
            "type": "question",
        },
        user_id="1",
    )

    assert new_ticket.id is not None
    assert new_ticket.subject == "New Ticket"
    assert new_ticket.description == "New Ticket description"


def test_create_ticket_with_no_subject(api_ticket_service, mock_data):
    with pytest.raises(BadRequestError):
        api_ticket_service.create_ticket(
            api_id=mock_data[5].id,
            ticket={
                "description": "New Ticket description",
                "type": "question",
            },
            user_id="1",
        )


def test_create_ticket_with_no_description(api_ticket_service, mock_data):
    with pytest.raises(BadRequestError):
        api_ticket_service.create_ticket(
            api_id=mock_data[5].id,
            ticket={
                "subject": "New Ticket",
                "type": "question",
            },
            user_id="1",
        )


def test_create_ticket_with_no_type(api_ticket_service, mock_data):
    with pytest.raises(BadRequestError):
        api_ticket_service.create_ticket(
            api_id=mock_data[5].id,
            ticket={
                "subject": "New Ticket",
                "description": "New Ticket description",
            },
            user_id="1",
        )


def test_create_ticket_of_unknown_api(api_ticket_service, mock_data):
    with pytest.raises(NotFoundError):
        api_ticket_service.create_ticket(
            api_id="999",
            ticket={
                "subject": "New Ticket",
                "description": "New Ticket description",
                "type": "question",
            },
            user_id="1",
        )
