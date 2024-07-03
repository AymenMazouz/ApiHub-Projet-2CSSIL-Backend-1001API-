from flask_restx import Namespace, fields


class AuthDto:
    api = Namespace("Auth", description="authentication related operations")

    user_login_request = api.model(
        "user_login",
        {
            "email": fields.String(required=True),
            "password": fields.String(required=True),
        },
    )

    user_login_response = api.model(
        "user_login_success",
        {"Authorization": fields.String()},
    )

    user_register_request = api.model(
        "user_register",
        {
            "email": fields.String(
                required=True,
            ),
            "password": fields.String(
                required=True,
            ),
            "firstname": fields.String(
                required=True,
            ),
            "lastname": fields.String(
                required=True,
            ),
        },
    )

    user_info_response = api.model(
        "user_info",
        {
            "data": fields.Nested(
                api.model(
                    "user_info_data",
                    {
                        "id": fields.Integer(),
                        "email": fields.String(),
                        "firstname": fields.String(),
                        "lastname": fields.String(),
                        "role": fields.String(),
                        "status": fields.String(),
                        "created_at": fields.DateTime(),
                        "updated_at": fields.DateTime(),
                        "avatar": fields.String(nullable=True),
                        "phone_number": fields.String(nullable=True),
                        "bio": fields.String(nullable=True),
                    },
                )
            ),
        },
    )

    user_info_update_request = api.model(
        "user_info_update",
        {
            "firstname": fields.String(),
            "lastname": fields.String(),
            "bio": fields.String(),
            "phone_number": fields.String(),
        },
    )
