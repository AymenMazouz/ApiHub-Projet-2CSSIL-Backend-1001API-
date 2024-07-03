import pytest
from app.main.core.services.user_service import UserService
from app.main.model.user_model import User
from .fixtures.user.add_user import add_user
from .fixtures.user.suspend_user import suspend_user
from .fixtures.media_manager_mock import MediaManagerMock
from faker import Faker
from app.main.utils.exceptions import NotFoundError
from app.main.utils.exceptions import BadRequestError
from app.main.utils.roles import Role


fake = Faker()

user_service = UserService(media_manager=MediaManagerMock())


def test_get_users_statistics(test_db):
    users_number = user_service.get_users_statistics()["users_number"]
    suppliers_number = user_service.get_users_statistics()["suppliers_number"]
    admins_number = user_service.get_users_statistics()["admins_number"]
    assert users_number == 0
    assert suppliers_number == 0
    assert admins_number == 1


def test_get_users(test_db):
    password = fake.password()
    new_user = add_user(
        db=test_db,
        email="New_user1@gmail.com",
        firstname="New User",
        lastname="New User",
        password=password,
    )
    query_params = {"page": 1, "per_page": 10, "status": "", "role": None}
    users_data, pagination_info = user_service.get_users(query_params)
    assert len(users_data) == 2
    assert users_data[1]["id"] == new_user.id


def test_get_user_by_id(test_db):
    password = fake.password()

    new_user = add_user(
        db=test_db,
        email="New_user2@gmail.com",
        firstname="New User",
        lastname="New User",
        password=password,
    )
    fetched_user_data = user_service.get_user_by_id(new_user.id)
    fetched_user_id = fetched_user_data["id"]
    assert fetched_user_id == new_user.id


def test_get_user_by_id_with_user_not_found(test_db):
    user_id = 99999

    with pytest.raises(NotFoundError):
        user_service.get_user_by_id(user_id)


def test_activate_user(test_db):
    password = fake.password()

    new_user = add_user(
        db=test_db,
        email="New_user@gmail.com",
        firstname="New User",
        lastname="New User",
        password=password,
    )
    user_id = new_user.id
    suspend_user(db=test_db, user_id=user_id)
    user_service.activate_user(user_id)
    activated_use = User.query.filter_by(id=user_id).first()
    assert activated_use.status == "active"


def test_activate_user_with_user_not_found(test_db):
    user_id = 99999

    with pytest.raises(NotFoundError):
        user_service.activate_user(user_id)


def test_suspend_user(test_db):
    password = fake.password()

    new_user = add_user(
        db=test_db,
        email="New_user3@gmail.com",
        firstname="New User",
        lastname="New User",
        password=password,
    )
    user_id = new_user.id
    user_service.suspend_user(user_id)
    suspended_use = User.query.filter_by(id=user_id).first()
    assert suspended_use.status == "suspended"


def test_suspend_user_with_user_not_found(test_db):
    user_id = 99999

    with pytest.raises(NotFoundError):
        user_service.suspend_user(user_id)


def test_create_supplier(test_db):
    data = {
        "email": "New_supplier@gmail.com",
        "password": "New supplier password",
        "firstname": "New supplier",
        "lastname": "New supplier",
    }
    user_id = user_service.create_supplier(data)

    user = User.query.filter_by(id=user_id).first()
    assert user.email == data["email"]
    assert user.role == Role.SUPPLIER


def test_create_supplier_with_user_already_exists(test_db):
    password = fake.password()
    add_user(
        db=test_db,
        email="Existed_supplier@gmail.com",
        firstname="Existed supplier",
        lastname="Existed supplier",
        password=password,
    )
    data = {
        "email": "Existed_supplier@gmail.com",
        "password": "Existed supplier password",
        "firstname": "Existed supplier",
        "lastname": "Existed supplier",
    }
    with pytest.raises(BadRequestError):
        user_service.create_supplier(data)


def test_create_supplier_with_invalid_email(test_db):
    data = {
        "email": "supplier invalide email",
        "password": "supplier password",
        "firstname": "supplier",
        "lastname": "supplier",
    }
    with pytest.raises(BadRequestError):
        user_service.create_supplier(data)


def test_edit_user(test_db):
    password = fake.password()
    new_user = add_user(
        db=test_db,
        email="New_user4@gmail.com",
        firstname="New User",
        lastname="New User",
        password=password,
    )
    user_id = new_user.id
    data = {
        "firstname": "Edited user",
        "lastname": "Edited user",
        "bio": "the user bio",
        "phone_number": "0775757899",
    }
    user_service.edit_user(user_id, data)

    edited_user = User.query.filter_by(id=user_id).first()
    assert edited_user.id == user_id
    assert edited_user.firstname == data["firstname"]
    assert edited_user.lastname == data["lastname"]


def test_edit_user_with_user_not_found(test_db):
    user_id = 99999
    data = {
        "firstname": "Edited user",
        "lastname": "Edited user",
        "bio": "the user bio",
        "phone_number": "0775757899",
    }

    with pytest.raises(NotFoundError):
        user_service.edit_user(user_id, data)
