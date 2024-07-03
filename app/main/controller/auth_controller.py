from flask import request, g as top_g, Response
from flask_restx import Resource


from app.main.controller.dtos.auth_dto import AuthDto

from http import HTTPStatus

from app.main.core import ServicesInitializer

from app.main.utils.decorators.auth import require_authentication


api = AuthDto.api


@api.route("/login")
class UserLogin(Resource):
    @api.doc("user login")
    @api.expect(AuthDto.user_login_request, validate=True)
    @api.response(HTTPStatus.OK, "Success", AuthDto.user_login_response)
    def post(self):
        return {
            "Authorization": ServicesInitializer.an_auth_service().login(request.json)
        }, HTTPStatus.OK


@api.route("/register")
class UserRegister(Resource):
    @api.doc("user register")
    @api.expect(AuthDto.user_register_request, validate=True)
    @api.response(HTTPStatus.CREATED, "Success", AuthDto.user_register_request)
    def post(self):
        ServicesInitializer.an_auth_service().register(request.json)
        return Response(status=HTTPStatus.CREATED)


@api.route("/me")
class UserInfo(Resource):
    @api.doc("user info")
    @api.response(HTTPStatus.OK, "Success", AuthDto.user_info_response)
    @require_authentication
    def get(self):
        user = ServicesInitializer.a_user_service().get_user_by_id(top_g.user.get("id"))

        return {"data": user}, HTTPStatus.OK

    @api.doc("update user info")
    @api.expect(AuthDto.user_info_update_request, validate=True)
    @api.response(HTTPStatus.OK, "Success")
    @require_authentication
    def patch(self):
        ServicesInitializer.a_user_service().edit_user(
            top_g.user.get("id"), request.json
        )
        return Response(status=HTTPStatus.OK)
