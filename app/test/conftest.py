from flask_restx import Api
from flask import Blueprint

import pytest

from app.main import create_app, db

from app.main.controller.auth_controller import api as auth_ns
from app.main.controller.user_controller import api as users_ns
from app.main.controller.api_controller import api as apis_ns


from app.main.model.user_model import User


blueprint = Blueprint("api", __name__)
authorizations = {"apikey": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(
    blueprint,
    title="ITOUCH API MARKETPLACE API DOCUMENTATION",
    version="1.0",
    description="ITOUCH API MARKETPLACE IS A PLATFORM THAT ALLOWS USERS TO CREATE, MANAGE AND MONETIZE THEIR API'S.",
    authorizations=authorizations,
    security="apikey",
)

api.add_namespace(auth_ns, path="/auth")
api.add_namespace(users_ns, path="/users")
api.add_namespace(apis_ns, path="/apis")


@pytest.fixture(scope="module")
def app():
    app = create_app("test")
    app.register_blueprint(blueprint)
    app.app_context().push()

    with app.app_context():
        db.create_all()

        User.create_default_admin()

        yield app
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(scope="module")
def test_db(app):
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()
