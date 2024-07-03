import pytest
from app.main.core import ServicesInitializer
from app.main.model.user_model import User
from .fixtures.user.add_user import add_user
from .fixtures.user.suspend_user import suspend_user
from faker import Faker
from app.main.utils.exceptions import NotFoundError
from app.main.utils.exceptions import BadRequestError


fake = Faker()
AuthService = ServicesInitializer.an_auth_service()


def test_register(test_db):
    data = {
        "email": "New_user@gmail.com",
        "password": "New User password",
        "firstname": "New User",
        "lastname": "New User",
    }
    user_id = AuthService.register(data)

    user = User.query.filter_by(id=user_id).first()
    assert user.email == data["email"]


def test_login(test_db):
    password = fake.password()

    new_user = add_user(
        db=test_db,
        email="New_user1@gmail.com",
        firstname="New User",
        lastname="New User",
        password=password,
    )
    login_data = {"email": new_user.email, "password": password}
    auth_token = AuthService.login(data=login_data)
    user_id = User.decode_auth_token(auth_token)
    assert user_id == new_user.id
    assert auth_token is not None


def test_login_with_user_not_found(test_db):
    password = fake.password()

    login_data = {"email": "user_not_found@gmail.com", "password": password}
    with pytest.raises(NotFoundError):
        AuthService.login(data=login_data)


def test_login_with_email_not_match(test_db):
    password = fake.password()

    new_user = add_user(
        db=test_db,
        email="New_user2@gmail.com",
        firstname="New User",
        lastname="New User",
        password=password,
    )
    login_data = {"email": new_user.email, "password": "wrong password"}
    with pytest.raises(BadRequestError):
        AuthService.login(data=login_data)


def test_login_with_user_not_active(test_db):
    password = fake.password()

    new_user = add_user(
        db=test_db,
        email="New_user3@gmail.com",
        firstname="New User",
        lastname="New User",
        password=password,
    )
    user_id = new_user.id
    user = suspend_user(db=test_db, user_id=user_id)
    login_data = {"email": user.email, "password": password}
    with pytest.raises(BadRequestError):
        AuthService.login(data=login_data)
