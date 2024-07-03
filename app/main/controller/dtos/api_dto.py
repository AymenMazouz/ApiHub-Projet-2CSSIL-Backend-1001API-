from flask_restx import Namespace, fields
from .user_dto import UserDto


class ApiDto:
    api_category = Namespace(
        "Api Category", description="api category related operations"
    )

    api = Namespace("Api", description="api related operations")

    api_tests = Namespace("Api Tests", description="api tests related operations")

    api_version = Namespace("Api Version", description="api version related operations")

    api_discussions = Namespace(
        "Api Discussions", description="api discussions related operations"
    )

    api_subscription = Namespace(
        "Api Subscription", description="api subscription related operations"
    )

    api_keys = Namespace("Api Keys", description="api keys related operations")

    api_calls = Namespace("Api Calls", description="api calls related operations")
    api_resquests = Namespace(
        "Api Requests", description="api requests related operations"
    )

    api_tickets = Namespace("Api Tickets", description="api tickets related operations")

    create_ticket_request = api_tickets.model(
        "create_ticket_request",
        {
            "subject": fields.String(
                required=True,
            ),
            "description": fields.String(
                required=True,
            ),
            "type": fields.String(
                required=True,
            ),
        },
    )

    respond_to_ticket_request = api_tickets.model(
        "respond_to_ticket_request",
        {
            "response": fields.String(
                required=True,
            ),
        },
    )

    api_keys_list_response = api_keys.model(
        "api_keys_list_response",
        {
            "data": fields.List(
                fields.Nested(
                    api_keys.model(
                        "api_keys_list_data",
                        {
                            "key": fields.String(),
                            "subscription_id": fields.Integer(),
                            "status": fields.String(),
                            "created_at": fields.DateTime(),
                        },
                    )
                )
            ),
        },
    )

    create_category_request = api.model(
        "create_category_request",
        {
            "name": fields.String(
                required=True,
            ),
            "description": fields.String(
                required=True,
            ),
        },
    )

    update_category_request = api.model(
        "update_category_request",
        {
            "name": fields.String(
                required=True,
            ),
            "description": fields.String(
                required=True,
            ),
        },
    )

    categories_list_response = api.model(
        "categories_list_response",
        {
            "data": fields.List(
                fields.Nested(
                    api.model(
                        "categories_list_data",
                        {
                            "id": fields.Integer(),
                            "name": fields.String(),
                            "description": fields.String(),
                            "created_by": fields.Integer(),
                            "created_at": fields.DateTime(),
                            "updated_at": fields.DateTime(),
                            "image": fields.String(),
                        },
                    )
                )
            ),
        },
    )

    category_info_response = api.model(
        "category_info",
        {
            "data": fields.Nested(
                api.model(
                    "category_info_data",
                    {
                        "id": fields.Integer(),
                        "name": fields.String(),
                        "description": fields.String(),
                        "created_by_id": fields.Integer(),
                        "created_by": fields.Nested(
                            api.model(
                                "category_creator_info_data",
                                {
                                    "id": fields.Integer(),
                                    "firstname": fields.String(),
                                    "lastname": fields.String(),
                                },
                            )
                        ),
                        "created_at": fields.DateTime(),
                        "updated_at": fields.DateTime(),
                        "image": fields.String(),
                    },
                ),
            ),
        },
    )

    create_api_request = api.model(
        "create_api_request",
        {
            "name": fields.String(
                required=True,
            ),
            "description": fields.String(
                required=True,
            ),
            "category_id": fields.Integer(
                required=True,
            ),
            "plans": fields.List(
                fields.Nested(
                    api.model(
                        "api_plan",
                        {
                            "name": fields.String(
                                required=True,
                            ),
                            "description": fields.String(
                                required=True,
                            ),
                            "price": fields.Integer(
                                required=True,
                            ),
                            "max_requests": fields.Integer(
                                required=True,
                            ),
                            "duration": fields.Integer(
                                required=True,
                            ),
                        },
                    )
                ),
                required=True,
            ),
        },
    )

    apis_list_response = api.model(
        "apis_list_response",
        {
            "data": fields.List(
                fields.Nested(
                    api.model(
                        "apis_list_data",
                        {
                            "id": fields.Integer(),
                            "name": fields.String(),
                            "description": fields.String(),
                            "category_id": fields.Integer(),
                            "category": fields.Nested(
                                api.model(
                                    "api_category_info_data",
                                    {
                                        "id": fields.Integer(),
                                        "name": fields.String(),
                                    },
                                )
                            ),
                            "supplier_id": fields.Integer(),
                            "supplier": fields.Nested(
                                api.model(
                                    "api_supplier_info_data",
                                    {
                                        "id": fields.Integer(),
                                        "firstname": fields.String(),
                                        "lastname": fields.String(),
                                    },
                                )
                            ),
                            "status": fields.String(),
                            "created_at": fields.DateTime(),
                            "updated_at": fields.DateTime(),
                            "image": fields.String(),
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

    update_api_request = api.model(
        "update_api_request",
        {
            "name": fields.String(),
            "description": fields.String(),
            "category_id": fields.Integer(),
        },
    )

    api_info_response = api.model(
        "api_info",
        {
            "data": fields.Nested(
                api.model(
                    "api_info_data",
                    {
                        "id": fields.Integer(),
                        "name": fields.String(),
                        "description": fields.String(),
                        "average_response_time": fields.Float(),
                        "category_id": fields.Integer(),
                        "category": fields.Nested(
                            api.model(
                                "api_category_info_data",
                                {
                                    "id": fields.Integer(),
                                    "name": fields.String(),
                                },
                            )
                        ),
                        "supplier_id": fields.Integer(),
                        "supplier": fields.Nested(
                            api.model(
                                "api_supplier_info_data",
                                {
                                    "id": fields.Integer(),
                                    "firstname": fields.String(),
                                    "lastname": fields.String(),
                                },
                            )
                        ),
                        "status": fields.String(),
                        "created_at": fields.DateTime(),
                        "updated_at": fields.DateTime(),
                        "image": fields.String(),
                        "plans": fields.List(
                            fields.Nested(
                                api.model(
                                    "api_plan",
                                    {
                                        "name": fields.String(),
                                        "description": fields.String(),
                                        "price": fields.Integer(),
                                        "max_requests": fields.Integer(),
                                        "duration": fields.Integer(),
                                    },
                                )
                            ),
                        ),
                    },
                ),
            ),
        },
    )

    apis_count_response = api.model(
        "api_count_response",
        {
            "apis_number": fields.Integer(),
        },
    )

    apis_users_count_response = api.model(
        "apis_users_count_response",
        {
            "users_number": fields.Integer(),
        },
    )

    api_total_revenue_response = api.model(
        "api_total_revenue_response",
        {"total_revenue": fields.Float()},
    )

    api_per_month_count_response = api.model(
        "apis_per_month_count_response",
        {
            "monthly_subscribers": fields.Integer(),
        },
    )

    api_endpoints_count_response = api.model(
        "api_endpoints_count_response",
        {
            "endpoints_number": fields.Integer(),
        },
    )

    api_service_level_response = api.model(
        "api_service_level_response",
        {
            "service_level": fields.Integer(),
        },
    )

    api_popularity_response = api.model(
        "api_popularity_response",
        {
            "popularity": fields.Integer(),
        },
    )

    api_total_revenue_response = api.model(
        "api_total_revenue_response",
        {
            "total_revenue": fields.Float(),
        },
    )

    api_average_successfully_response_time_response = api.model(
        "api_average_successfully_response_time_response",
        {
            "average_successfully_response_time": fields.Float(),
        },
    )

    api_total_apis_count_response = api.model(
        "api_total_apis_count_response",
        {
            "total_apis_count": fields.Integer(),
        },
    )

    api_total_transactions_by_month_response = api.model(
        "api_total_transactions_response",
        {
            "data": fields.List(
                fields.Nested(
                    api.model(
                        "monthly_transaction_response",
                        {
                            "year": fields.Integer(),
                            "month": fields.Integer(),
                            "total_transactions": fields.Float(),
                        },
                    )
                )
            )
        },
    )

    api_total_transactions_by_day_response = api.model(
        "api_total_transactions_by_day_response",
        {
            "data": fields.List(
                fields.Nested(
                    api.model(
                        "dayly_transaction_response",
                        {
                            "year": fields.Integer(),
                            "month": fields.Integer(),
                            "day": fields.Integer(),
                            "total_transactions": fields.Float(),
                        },
                    )
                )
            )
        },
    )

    api_total_transactions_by_hour_response = api.model(
        "api_total_transactions_by_hour_response",
        {
            "data": fields.List(
                fields.Nested(
                    api.model(
                        "by_hour_transaction_response",
                        {
                            "year": fields.Integer(),
                            "month": fields.Integer(),
                            "day": fields.Integer(),
                            "hour": fields.Integer(),
                            "total_transactions": fields.Float(),
                        },
                    )
                )
            )
        },
    )

    apis_total_revenue_response = api.model(
        "apis_total_revenue_response",
        {
            "total_revenue": fields.Integer(),
        },
    )

    create_api_version_request = api.model(
        "create_api_version",
        {
            "version": fields.String(
                required=True,
            ),
            "base_url": fields.String(
                required=True,
            ),
            "headers": fields.List(
                fields.Nested(
                    api.model(
                        "api_header",
                        {
                            "key": fields.String(
                                required=True,
                            ),
                            "value": fields.String(
                                required=True,
                            ),
                        },
                    )
                ),
                required=True,
            ),
            "endpoints": fields.List(
                fields.Nested(
                    api.model(
                        "api_endpoint",
                        {
                            "url": fields.String(
                                required=True,
                            ),
                            "method": fields.String(
                                required=True,
                            ),
                            "description": fields.String(
                                required=True,
                            ),
                            "request_body": fields.String(
                                required=True,
                            ),
                            "response_body": fields.String(
                                required=True,
                            ),
                        },
                    )
                ),
                required=True,
            ),
        },
    )

    api_versions_list_response = api.model(
        "api_versions_list_response",
        {
            "data": fields.List(
                fields.Nested(
                    api.model(
                        "api_versions_list_data",
                        {
                            "version": fields.String(),
                            "status": fields.String(),
                            "created_at": fields.DateTime(),
                            "updated_at": fields.DateTime(),
                        },
                    )
                )
            ),
        },
    )

    api_version_info_response = api.model(
        "api_version_info",
        {
            "data": fields.Nested(
                api.model(
                    "api_version_info_data",
                    {
                        "version": fields.String(),
                        "status": fields.String(),
                        "average_response_time": fields.Float(),
                        "created_at": fields.DateTime(),
                        "updated_at": fields.DateTime(),
                        "api": fields.Nested(
                            api.model(
                                "api_info_summary_data",
                                {
                                    "id": fields.Integer(),
                                    "name": fields.String(),
                                },
                            )
                        ),
                        "endpoints": fields.List(
                            fields.Nested(
                                api.model(
                                    "api_version_endpoints",
                                    {
                                        "endpoint": fields.String(),
                                        "method": fields.String(),
                                        "description": fields.String(),
                                        "request_body": fields.String(),
                                        "response_body": fields.String(),
                                    },
                                )
                            ),
                        ),
                    },
                )
            ),
        },
    )

    full_api_version_info_response = api.model(
        "full_api_version_info",
        {
            "data": fields.Nested(
                api.model(
                    "full_api_version_info_data",
                    {
                        "version": fields.String(),
                        "status": fields.String(),
                        "average_response_time": fields.Float(),
                        "base_url": fields.String(),
                        "created_at": fields.DateTime(),
                        "updated_at": fields.DateTime(),
                        "api": fields.Nested(
                            api.model(
                                "api_info_summary_data",
                                {
                                    "id": fields.Integer(),
                                    "name": fields.String(),
                                },
                            )
                        ),
                        "endpoints": fields.List(
                            fields.Nested(
                                api.model(
                                    "full_api_version_endpoints",
                                    {
                                        "endpoint": fields.String(),
                                        "method": fields.String(),
                                        "description": fields.String(),
                                        "request_body": fields.String(),
                                        "response_body": fields.String(),
                                    },
                                )
                            ),
                            description="List of endpoints associated with the API version",
                        ),
                        "headers": fields.List(
                            fields.Nested(
                                api.model(
                                    "full_api_version_headers",
                                    {
                                        "id": fields.Integer(),
                                        "key": fields.String(),
                                        "value": fields.String(),
                                        "created_at": fields.DateTime(),
                                        "updated_at": fields.DateTime(),
                                    },
                                )
                            )
                        ),
                    },
                )
            ),
        },
    )

    create_charigly_checkout_response = api.model(
        "create_charigly_checkout_response",
        {
            "checkout_url": fields.String(),
        },
    )

    subscription_info_response = api.model(
        "subscription_info",
        {
            "data": fields.Nested(
                api.model(
                    "subscription_info_data",
                    {
                        "id": fields.Integer(),
                        "api_id": fields.Integer(),
                        "api": fields.Nested(
                            api.model(
                                "subscription_api_info_data",
                                {
                                    "id": fields.Integer(),
                                    "name": fields.String(),
                                    "supplier_id": fields.Integer(),
                                },
                            )
                        ),
                        "api_plan": fields.String(),
                        "user_id": fields.Integer(),
                        "user": fields.Nested(
                            api.model(
                                "api_user_info_data",
                                {
                                    "id": fields.Integer(),
                                    "firstname": fields.String(),
                                    "lastname": fields.String(),
                                },
                            )
                        ),
                        "start_date": fields.DateTime(),
                        "end_date": fields.DateTime(),
                        "remaining_requests": fields.Integer(),
                        "status": fields.String(),
                        "expired": fields.Boolean(),
                        "price": fields.Float(),
                    },
                )
            ),
        },
    )

    subscriptions_list_response = api.model(
        "subscriptions_list_response",
        {
            "data": fields.List(
                fields.Nested(
                    api.model(
                        "subscriptions_list_data",
                        {
                            "id": fields.Integer(),
                            "api_id": fields.Integer(),
                            "api": fields.Nested(
                                api.model(
                                    "subscription_api_info_data",
                                    {
                                        "id": fields.Integer(),
                                        "name": fields.String(),
                                        "supplier_id": fields.Integer(),
                                    },
                                )
                            ),
                            "api_plan": fields.String(),
                            "user_id": fields.Integer(),
                            "user": fields.Nested(
                                api.model(
                                    "api_user_info_data",
                                    {
                                        "id": fields.Integer(),
                                        "firstname": fields.String(),
                                        "lastname": fields.String(),
                                    },
                                )
                            ),
                            "start_date": fields.DateTime(),
                            "end_date": fields.DateTime(),
                            "remaining_requests": fields.Integer(),
                            "status": fields.String(),
                            "expired": fields.Boolean(),
                            "price": fields.Float(),
                        },
                    )
                )
            ),
            "pagination": fields.Nested(
                api.model(
                    "subscriptions_list_pagination",
                    {
                        "page": fields.Integer(),
                        "per_page": fields.Integer(),
                        "total": fields.Integer(),
                        "total_pages": fields.Integer(),
                    },
                )
            ),
        },
    )

    subscriptions_per_day_list_response = api.model(
        "subscriptions_per_day_list_response",
        {
            "data": fields.List(
                fields.Nested(
                    api.model(
                        "subscriptions_per_day_list_data",
                        {
                            "date": fields.DateTime(),
                            "count": fields.Integer(),
                        },
                    )
                )
            ),
        },
    )

    api_total_subscription_revenue_by_month_response = api.model(
        "api_total_subscription_revenue_by_month_response",
        {
            "data": fields.List(
                fields.Nested(
                    api.model(
                        "monthly_subscription_revenue_response",
                        {
                            "year": fields.Integer(),
                            "month": fields.Integer(),
                            "total_revenues": fields.Float(),
                        },
                    )
                )
            )
        },
    )

    api_total_subscription_revenue_by_day_response = api.model(
        "api_total_subscription_revenue_by_day_response",
        {
            "data": fields.List(
                fields.Nested(
                    api.model(
                        "mdayly_subscription_revenue_response",
                        {
                            "year": fields.Integer(),
                            "month": fields.Integer(),
                            "day": fields.Integer(),
                            "total_revenues": fields.Float(),
                        },
                    )
                )
            )
        },
    )

    api_total_subscription_revenue_by_hour_response = api.model(
        "api_total_subscription_revenue_by_hour_response",
        {
            "data": fields.List(
                fields.Nested(
                    api.model(
                        "by_hour_subscription_revenue_response",
                        {
                            "year": fields.Integer(),
                            "month": fields.Integer(),
                            "day": fields.Integer(),
                            "hour": fields.Integer(),
                            "total_revenues": fields.Float(),
                        },
                    )
                )
            )
        },
    )

    activate_api_key_request = api.model(
        "activate_api_key_request",
        {
            "key": fields.String(
                required=True,
            ),
        },
    )

    deactivate_api_key_request = api.model(
        "deactivate_api_key_request",
        {
            "key": fields.String(
                required=True,
            ),
        },
    )
    # ------------------- UN REFACTORED -------------------

    discussions_response = api.model(
        "discussions_response",
        {
            "id": fields.Integer(description="The unique identifier of the discussion"),
            "title": fields.String(
                required=True, description="The title of the discussion"
            ),
            "user": fields.Nested(
                description="The user who created the discussion",
                model=UserDto.nested_user_info_response,
            ),
            "created_at": fields.DateTime(
                description="The date and time when the discussion was created"
            ),
            "api_id": fields.Integer(
                required=True, description="The API ID associated with the discussion"
            ),
        },
    )

    create_discussion_request = api.model(
        "create_discussion_request",
        {
            "title": fields.String(
                required=True, description="The title of the discussion"
            ),
            "question": fields.String(
                required=True, description="The question of the discussion"
            ),
        },
    )

    discussion_answer_response = api.model(
        "create_discussion_answer_response",
        {
            "id": fields.Integer(description="The unique identifier of the answer"),
            "discussion_id": fields.Integer(
                description="The unique identifier of the discussion"
            ),
            "user": fields.Nested(
                description="The user who created the answer",
                model=UserDto.nested_user_info_response,
            ),
            "answer": fields.String(description="The answer of the discussion"),
            "created_at": fields.DateTime(
                description="The date and time when the answer was created"
            ),
            "votes": fields.Integer(
                description="The number of votes of the answer", attribute="votes_count"
            ),
        },
    )
    discussion_details_response = api.model(
        "discussion_details_response",
        {
            "id": fields.Integer(description="The unique identifier of the discussion"),
            "title": fields.String(
                required=True, description="The title of the discussion"
            ),
            "question": fields.String(
                required=True, description="The question of the discussion"
            ),
            "user": fields.Nested(
                description="The user who created the answer",
                model=UserDto.nested_user_info_response,
            ),
            "created_at": fields.DateTime(
                description="The date and time when the discussion was created"
            ),
            "api_id": fields.Integer(
                required=True, description="The API ID associated with the discussion"
            ),
            "answers": fields.List(fields.Nested(discussion_answer_response)),
        },
    )

    create_discussion_answer_request = api.model(
        "create_discussion_answer_request",
        {
            "answer": fields.String(
                required=True, description="The answer of the discussion"
            ),
        },
    )

    create_vote_request = api.model(
        "create_vote_request",
        {
            "vote": fields.String(
                required=True, description="The vote of the answer", enum=["up", "down"]
            ),
        },
    )

    user_vote_response = api.model(
        "user vote response",
        {
            "user_id": fields.Integer(),
            "answer_id": fields.Integer(),
            "vote": fields.String(),
        },
    )

    requests_list_response = api.model(
        "requests_list_response",
        {
            "data": fields.List(
                fields.Nested(
                    api.model(
                        "requests_list_data",
                        {
                            "id": fields.Integer(),
                            "api_id": fields.Integer(),
                            "api": fields.Nested(
                                api.model(
                                    "api_info_data",
                                    {
                                        "id": fields.Integer(),
                                        "name": fields.String(),
                                        "supplier_id": fields.Integer(),
                                    },
                                )
                            ),
                            "api_version": fields.String(),
                            "user_id": fields.Integer(),
                            "user": fields.Nested(
                                api.model(
                                    "api_user_info_data",
                                    {
                                        "id": fields.Integer(),
                                        "firstname": fields.String(),
                                        "lastname": fields.String(),
                                    },
                                )
                            ),
                            "request_url": fields.String(),
                            "request_method": fields.String(),
                            "http_status": fields.Integer(),
                            "request_at": fields.DateTime(),
                            "response_at": fields.DateTime(),
                            "response_time": fields.Integer(),
                        },
                    )
                )
            ),
            "pagination": fields.Nested(
                api.model(
                    "requests_list_pagination",
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
