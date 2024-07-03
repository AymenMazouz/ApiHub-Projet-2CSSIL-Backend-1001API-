from flask_restx import Api
from http import HTTPStatus
from .exceptions import NotFoundError, BadRequestError


def register_error_handlers(api: Api):
    @api.errorhandler(NotFoundError)
    def handle_not_found_exception(error: NotFoundError):
        return {"message": error.message}, HTTPStatus.NOT_FOUND

    @api.errorhandler(BadRequestError)
    def handle_bad_request_exception(error: BadRequestError):
        return {"message": error.message}, HTTPStatus.BAD_REQUEST

    @api.errorhandler(Exception)
    def handle_generic_exception(error):
        print(error)

        return (
            {"message": "Internal server error"},
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
