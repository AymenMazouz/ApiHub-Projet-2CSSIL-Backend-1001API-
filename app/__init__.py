import os
from app.main import create_app

from flask_restx import Api
from flask import Blueprint, Response, request
from flask_cors import CORS

from app.main.controller.auth_controller import api as auth_ns
from app.main.controller.user_controller import api as users_ns
from app.main.controller.api_controller import api as api_ns
from app.main.controller.api_controller import api_category as api_category_ns
from app.main.controller.api_controller import api_tests as api_tests_ns
from app.main.controller.api_controller import api_version as api_version_ns
from app.main.controller.api_controller import api_discussions as api_discussions_ns
from app.main.controller.api_controller import api_subscription as api_subscription_ns
from app.main.controller.api_controller import api_keys as api_keys_ns
from app.main.controller.api_controller import api_calls as api_calls_ns
from app.main.controller.api_controller import api_resquests as api_requests_ns
from app.main.controller.api_controller import api_tickets as api_tickets_ns


from app.main.utils.error_handlers import register_error_handlers

from app.main.core.lib.impl.file_logger import FileLogger

# import models to let the migrate tool know
from app.main.model.user_model import User
from app.main.model.api_model import ApiModel  # noqa: F401
from app.main.model.api_category_model import ApiCategory  # noqa: F401
from app.main.model.api_version_model import ApiVersion  # noqa: F401
from app.main.model.api_plan_model import ApiPlan  # noqa: F401
from app.main.model.api_header_model import ApiVersionHeader  # noqa: F401
from app.main.model.api_version_endpoint_model import ApiVersionEndpoint  # noqa: F401
from app.main.model.api_key_model import ApiKey  # noqa: F401
from app.main.model.api_subscription_model import ApiSubscription  # noqa: F401
from app.main.model.api_request_model import ApiRequest  # noqa: F401
from app.main.model.api_ticket_model import ApiTicket  # noqa: F401
from logtail import LogtailHandler
import logging

blueprint = Blueprint("api", __name__)
authorizations = {"apikey": {"type": "apiKey", "in": "header", "name": "Authorization"}}
file_logger = FileLogger()

api = Api(
    blueprint,
    title="ITOUCH API MARKETPLACE API",
    version="1.0",
    description="ITOUCH API MARKETPLACE IS A PLATFORM THAT ALLOWS USERS TO CREATE, MANAGE AND MONETIZE THEIR API'S.",
    authorizations=authorizations,
    security="apikey",
)

api.add_namespace(auth_ns, path="/auth")
api.add_namespace(users_ns, path="/users")
api.add_namespace(api_ns, path="/apis")
api.add_namespace(api_category_ns, path="/apis")
api.add_namespace(api_tests_ns, path="/apis")
api.add_namespace(api_version_ns, path="/apis")
api.add_namespace(api_discussions_ns, path="/apis")
api.add_namespace(api_subscription_ns, path="/apis")
api.add_namespace(api_keys_ns, path="/apis")
api.add_namespace(api_calls_ns, path="/apis")
api.add_namespace(api_requests_ns, path="/apis")
api.add_namespace(api_tickets_ns, path="/apis")

app = create_app(os.getenv("FLASK_ENV", "dev"))
CORS(app)
app.register_blueprint(blueprint)
app.app_context().push()

register_error_handlers(api)

with app.app_context():
    User.create_default_admin()

handler = LogtailHandler(
    source_token=os.getenv("SOURCE_TOKEN", "WhMxdjaNXfNUVQtHSvWbx9iq")
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.handlers = []
logger.addHandler(handler)


@app.after_request
def after_request(response: Response):
    if response.status_code >= 400:
        file_logger.error(
            "HTTP Request",
            {
                "path": request.path,
                "method": request.method,
                "status_code": response.status_code,
                "response": response.get_json(),
            },
        )
        logger.error(
            "HTTP Request Error",
            extra={
                "path": request.path,
                "method": request.method,
                "status_code": response.status_code,
                "response": response.get_json(),
            },
        )
    else:
        file_logger.info(
            "HTTP Request",
            {
                "path": request.path,
                "method": request.method,
                "status_code": response.status_code,
                "response": response.get_json(),
            },
        )
        logger.info(
            "HTTP Request Success",
            extra={
                "path": request.path,
                "method": request.method,
                "status_code": response.status_code,
                "response": response.get_json(),
            },
        )

    return response
