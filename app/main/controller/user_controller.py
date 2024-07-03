from flask import request, Response
from flask_restx import Resource

from app.main.controller.dtos.user_dto import UserDto

from app.main.utils.decorators.auth import role_token_required

from app.main.core import ServicesInitializer
from http import HTTPStatus

from app.main.utils.roles import Role

api = UserDto.api


@api.route("/<int:user_id>")
class UserInfo(Resource):
    @api.doc("user info")
    @api.response(HTTPStatus.OK, "Success", UserDto.user_info_response)
    @role_token_required([Role.ADMIN])
    def get(self, user_id: int):

        return {
            "data": ServicesInitializer.a_user_service().get_user_by_id(user_id)
        }, HTTPStatus.OK


@api.route("/")
class UsersList(Resource):
    @api.doc("list of registered users")
    @api.param("page", "The page number")
    @api.param("per_page", "The number of items per page")
    @api.param("roles", "The roles", type="array")
    @api.param("status", "The status of the apis")
    @api.response(HTTPStatus.OK, "Success", UserDto.users_list_response)
    @role_token_required([Role.ADMIN])
    def get(self):
        users, pagination = ServicesInitializer.a_user_service().get_users(request.args)
        return {"data": users, "pagination": pagination}, HTTPStatus.OK


@api.route("/<int:user_id>/suspend")
class SuspendUser(Resource):
    @api.doc("suspend user")
    @api.response(HTTPStatus.OK, "Success")
    @role_token_required([Role.ADMIN])
    def patch(self, user_id: int):
        ServicesInitializer.a_user_service().suspend_user(user_id)
        return Response(status=HTTPStatus.OK)


@api.route("/<int:user_id>/activate")
class ActivateUser(Resource):
    @api.doc("activate user")
    @api.response(HTTPStatus.OK, "Success")
    @role_token_required([Role.ADMIN])
    def patch(self, user_id: int):
        ServicesInitializer.a_user_service().activate_user(user_id)
        return Response(status=HTTPStatus.OK)


@api.route("/suppliers")
class NewSupplier(Resource):
    @api.doc("Create supplier")
    @api.expect(UserDto.new_supplier_request, validate=True)
    @api.response(HTTPStatus.CREATED, "success")
    @role_token_required([Role.ADMIN])
    def post(self):
        ServicesInitializer.a_user_service().create_supplier(request.json)
        return Response(status=HTTPStatus.CREATED)


@api.route("/statistics")
class GetUsersStatistics(Resource):
    @api.doc("Get Users Number")
    @api.response(HTTPStatus.OK, "success", UserDto.user_statistics_response)
    @role_token_required([Role.ADMIN])
    def get(self):
        users_number = ServicesInitializer.a_user_service().get_users_statistics()
        return {"data": users_number}, HTTPStatus.OK
