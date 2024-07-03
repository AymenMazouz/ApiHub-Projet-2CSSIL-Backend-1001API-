from flask_restx import Namespace, fields


class UserDto:
    api = Namespace("User", description="user related operations")

    user_info_response = api.model(
        "single_user_info",
        {
            "data": fields.Nested(
                api.model(
                    "single_user_info_data",
                    {
                        "id": fields.Integer(),
                        "email": fields.String(),
                        "role": fields.String(),
                        "firstname": fields.String(),
                        "lastname": fields.String(),
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
    # dont touch it
    nested_user_info_response = api.model(
        "single_user_info",
        {
            "id": fields.Integer(),
            "email": fields.String(),
            "role": fields.String(),
            "firstname": fields.String(),
            "lastname": fields.String(),
            "status": fields.String(),
            "created_at": fields.DateTime(),
            "updated_at": fields.DateTime(),
            "avatar": fields.String(nullable=True),
        },
    )

    users_list_response = api.model(
        "users_list_response",
        {
            "data": fields.List(
                fields.Nested(
                    api.model(
                        "users_list_data",
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
                )
            ),
            "pagination": fields.Nested(
                api.model(
                    "users_list_pagination",
                    {
                        "page": fields.Integer(),
                        "per_page": fields.Integer(),
                        "total": fields.Integer(),
                        "pages": fields.Integer(),
                    },
                )
            ),
        },
    )

    new_supplier_request = api.model(
        "new_supplier_request",
        {
            "email": fields.String(
                required=True,
            ),
            "password": fields.String(required=True, description="The user password"),
            "firstname": fields.String(required=True, description="The user firstname"),
            "lastname": fields.String(required=True, description="The user lastname"),
        },
    )

    user_statistics_response = api.model(
        "user_statistics_response",
        {
            "users_number": fields.Integer(),
            "suppliers_number": fields.Integer(),
            "admins_number": fields.Integer(),
        },
    )
