from flask import request, g as top_g, Response
from flask_restx import Resource

from app.main.controller.dtos.api_dto import ApiDto

from app.main.utils.decorators.auth import role_token_required, require_authentication
from app.main.utils.decorators.discussion import (
    check_delete_discussion_permission,
    check_delete_answer_permission,
)

from app.main.utils.roles import Role

from app.main.core import ServicesInitializer

from http import HTTPStatus

api_category = ApiDto.api_category
api = ApiDto.api
api_tests = ApiDto.api_tests
api_version = ApiDto.api_version
api_discussions = ApiDto.api_discussions
api_subscription = ApiDto.api_subscription
api_keys = ApiDto.api_keys
api_calls = ApiDto.api_calls
api_resquests = ApiDto.api_resquests
api_tickets = ApiDto.api_tickets


@api_category.route("/categories/create")
class CreateCategory(Resource):
    @api_category.doc("create category")
    @api_category.expect(ApiDto.create_category_request, validate=True)
    @api_category.response(HTTPStatus.CREATED, "success")
    @role_token_required([Role.ADMIN])
    def post(self):
        ServicesInitializer.an_api_category_service().create_category(
            request.json, top_g.user.get("id")
        )
        return Response(status=HTTPStatus.CREATED)


@api_category.route("/categories")
class GetCategories(Resource):
    @api_category.doc("get categories")
    @api_category.response(HTTPStatus.OK, "Success", ApiDto.categories_list_response)
    def get(self):
        categories = ServicesInitializer.an_api_category_service().get_all_categories()

        return {
            "data": categories,
        }, HTTPStatus.OK


@api_category.route("/categories/<int:id>")
class GetCategoryById(Resource):
    @api_category.doc("get categorie by id")
    @api_category.response(HTTPStatus.OK, "Success", ApiDto.category_info_response)
    def get(self, id):
        categorie_data = (
            ServicesInitializer.an_api_category_service().get_category_by_id(id)
        )

        return {
            "data": categorie_data,
        }, HTTPStatus.OK


@api_category.route("/categories/<int:id>/update")
class UpdateCategory(Resource):
    @api_category.doc("create category")
    @api_category.expect(ApiDto.update_category_request, validate=True)
    @api_category.response(HTTPStatus.OK, "success")
    @role_token_required([Role.ADMIN])
    def patch(self, id):
        ServicesInitializer.an_api_category_service().update_category(
            request.json, category_id=id
        )
        return Response(status=HTTPStatus.OK)


@api.route("/create")
class CreateApi(Resource):
    @api.doc("create api")
    @api.expect(ApiDto.create_api_request, validate=True)
    @api.response(HTTPStatus.CREATED, "Success")
    @role_token_required([Role.SUPPLIER])
    def post(self):
        ServicesInitializer.an_api_service().create_api(
            request.json, top_g.user.get("id")
        )
        return Response(status=HTTPStatus.CREATED)


@api.route("/")
class GetApis(Resource):
    @api.doc("get apis")
    @api.param("page", "The page number")
    @api.param("per_page", "The number of items per page")
    @api.param("categoryIds", "The category ID", type="array")
    @api.param("status", "The status of the apis")
    @api.param("supplierId", "The supplier id")
    @api.param("search", "The search query")
    @api.response(HTTPStatus.OK, "Success", ApiDto.apis_list_response)
    def get(self):
        apis, pagination = ServicesInitializer.an_api_service().get_apis(request.args)
        return {
            "data": apis,
            "pagination": pagination,
        }, HTTPStatus.OK


@api.route("/mine")
class GetMyApis(Resource):
    @api.doc("get my apis")
    @api.param("page", "The page number")
    @api.param("per_page", "The number of items per page")
    @api.param("category_ids", "The category ID", type="array")
    @api.param("status", "The status of the apis")
    @api.param("search", "The search query")
    @api.response(HTTPStatus.OK, "Success", ApiDto.apis_list_response)
    @role_token_required([Role.SUPPLIER])
    def get(self):
        apis, pagination = ServicesInitializer.an_api_service().get_apis(
            {**request.args, "supplierId": top_g.user.get("id")}
        )
        return {
            "data": apis,
            "pagination": pagination,
        }, HTTPStatus.OK


@api.route("/<int:id>/update")
class UpdateApi(Resource):
    @api.doc("update api")
    @api.expect(ApiDto.update_api_request, validate=True)
    @api.response(HTTPStatus.OK, "Success")
    @role_token_required([Role.SUPPLIER])
    def patch(self, id):
        ServicesInitializer.an_api_service().update_api(
            id, top_g.user.get("id"), request.json
        )
        return Response(status=HTTPStatus.OK)


@api.route("/<int:id>")
class GetApiById(Resource):
    @api.doc("get api by id")
    @api.response(HTTPStatus.OK, "Success", ApiDto.api_info_response)
    def get(self, id):
        api_data = ServicesInitializer.an_api_service().get_api_by_id(id)
        return {
            "data": api_data,
        }, HTTPStatus.OK


@api.route("/mine/<int:id>")
class GetMyApiById(Resource):
    @api.doc("get my api by id")
    @api.response(HTTPStatus.OK, "Success", ApiDto.api_info_response)
    @role_token_required([Role.SUPPLIER])
    def get(self, id):
        api_data = ServicesInitializer.an_api_service().get_api_by_id(id)
        return {
            "data": api_data,
        }, HTTPStatus.OK


@api.route("/<int:id>/activate")
class ActivateApi(Resource):
    @api.doc("activate api")
    @api.response(HTTPStatus.OK, "Success")
    @role_token_required([Role.SUPPLIER, Role.ADMIN])
    def patch(self, id):
        ServicesInitializer.an_api_service().activate_api(
            api_id=id, user_id=top_g.user.get("id"), role=top_g.user.get("role")
        )
        return Response(status=HTTPStatus.OK)


@api.route("/<int:id>/deactivate")
class DeactivateApi(Resource):
    @api.doc("deactivate api")
    @api.response(HTTPStatus.OK, "Success")
    @role_token_required([Role.SUPPLIER, Role.ADMIN])
    def patch(self, id):
        ServicesInitializer.an_api_service().deactivate_api(
            api_id=id, user_id=top_g.user.get("id"), role=top_g.user.get("role")
        )
        return Response(status=HTTPStatus.OK)


@api.route("/mine/count")
class GetMyApisCount(Resource):
    @api.doc("get my apis count")
    @api.response(HTTPStatus.OK, "Success", ApiDto.apis_count_response)
    @role_token_required([Role.SUPPLIER])
    def get(self):
        apis_count = ServicesInitializer.an_api_service().get_apis_count(
            supplier_id=top_g.user.get("id")
        )
        return {
            "data": apis_count,
        }, HTTPStatus.OK


@api.route("/mine/users/count")
class GetMyApisUsersCount(Resource):
    @api.doc("get my apis  users count")
    @api.response(HTTPStatus.OK, "Success", ApiDto.apis_users_count_response)
    @role_token_required([Role.SUPPLIER])
    def get(self):
        users_count = ServicesInitializer.an_api_service().get_users_count(
            supplier_id=top_g.user.get("id")
        )
        return {
            "data": users_count,
        }, HTTPStatus.OK


@api.route("/mine/revenue")
class GetMyApisSubscriptionsRevenue(Resource):
    @api.doc("get my apis  subscription revenue")
    @api.response(HTTPStatus.OK, "Success", ApiDto.api_total_revenue_response)
    @role_token_required([Role.SUPPLIER])
    def get(self):
        total_revenue = (
            ServicesInitializer.an_api_service().get_active_subscriptions_count(
                supplier_id=top_g.user.get("id")
            )
        )
        return {
            "data": total_revenue,
        }, HTTPStatus.OK


@api.route("/mine/<int:id>/users/count")
class GetMyApiMonthlySubscribers(Resource):
    @api.doc("get my api monthly subscribers")
    @api.param("year", "The year of the subscription")
    @api.param("month", "The month of the subscription")
    @api.response(HTTPStatus.OK, "Success", ApiDto.apis_users_count_response)
    @role_token_required([Role.SUPPLIER])
    def get(self, id):
        users_count = ServicesInitializer.an_api_service().get_api_monthly_subscribers(
            {**request.args}, api_id=id
        )
        return {
            "data": users_count,
        }, HTTPStatus.OK


@api.route("/mine/<int:id>/endpoints/count")
class GetMyApiEndpointsCount(Resource):
    @api.doc("get my api endpoints count")
    @api.response(HTTPStatus.OK, "Success", ApiDto.api_endpoints_count_response)
    @role_token_required([Role.SUPPLIER])
    def get(self, id):
        endpoints_count = ServicesInitializer.an_api_service().get_endpoints_count(
            api_id=id
        )
        return {
            "data": endpoints_count,
        }, HTTPStatus.OK


@api.route("/mine/<int:id>/service-level")
class GetMyApiServiceLevel(Resource):
    @api.doc("get my api service level")
    @api.response(HTTPStatus.OK, "Success", ApiDto.api_service_level_response)
    def get(self, id):
        service_level = ServicesInitializer.an_api_service().get_api_service_level(
            api_id=id
        )
        return {
            "data": service_level,
        }, HTTPStatus.OK


@api.route("/mine/<int:id>/popularity")
class GetMyApiPopularity(Resource):
    @api.doc("get my api popularity")
    @api.response(HTTPStatus.OK, "Success", ApiDto.api_popularity_response)
    def get(self, id):
        popularity = ServicesInitializer.an_api_service().get_api_popularity(api_id=id)
        return {
            "data": popularity,
        }, HTTPStatus.OK


@api.route("/mine/<int:id>/revenue")
class GetMyApiMonthlyRevenue(Resource):
    @api.doc("get my api monthly revenue")
    @api.param("year", "The year of the subscription")
    @api.param("month", "The month of the subscription")
    @api.response(HTTPStatus.OK, "Success", ApiDto.api_total_revenue_response)
    @role_token_required([Role.SUPPLIER])
    def get(self, id):
        revenue = ServicesInitializer.an_api_service().get_api_monthly_revenue(
            {**request.args}, api_id=id
        )
        return {
            "data": revenue,
        }, HTTPStatus.OK


@api.route("/mine/<int:id>/avg-succ-response-time")
class GetMyApiAverageSuccessfullyResponseTime(Resource):
    @api.doc("get my api avrage successfull response time")
    @api.response(
        HTTPStatus.OK, "Success", ApiDto.api_average_successfully_response_time_response
    )
    def get(self, id):
        average_time = ServicesInitializer.an_api_service().get_api_average_successfully_response_time(
            api_id=id
        )
        return {
            "data": average_time,
        }, HTTPStatus.OK


@api.route("/count")
class GetTotalApisCount(Resource):
    @api.doc("get the total apis count")
    @api.response(HTTPStatus.OK, "Success", ApiDto.api_total_apis_count_response)
    @role_token_required([Role.ADMIN])
    def get(self):
        total_apis = ServicesInitializer.an_api_service().get_total_apis_count()
        return {
            "data": total_apis,
        }, HTTPStatus.OK


@api_version.route("/<int:id>/versions/create")
class CreateVersion(Resource):
    @api_version.doc("create version")
    @api_version.expect(ApiDto.create_api_version_request, validate=True)
    @api_version.response(HTTPStatus.CREATED, "Success")
    @role_token_required([Role.SUPPLIER])
    def post(self, id):
        ServicesInitializer.an_api_version_service().create_api_version(
            api_id=id, data=request.json, supplier_id=top_g.user.get("id")
        )
        return Response(status=HTTPStatus.CREATED)


@api_version.route("/<int:id>/versions")
class GetVersions(Resource):
    @api_version.doc("get versions")
    @api_version.param("status", "The status of the api versions")
    @api_version.response(HTTPStatus.OK, "Success", ApiDto.api_versions_list_response)
    def get(self, id):
        versions = ServicesInitializer.an_api_version_service().get_api_versions(
            api_id=id, query_params=request.args
        )

        return {
            "data": versions,
        }, HTTPStatus.OK


@api_version.route("/<int:id>/versions/<string:version>")
class GetVersion(Resource):
    @api_version.doc("get version")
    @api_version.response(HTTPStatus.OK, "Success", ApiDto.api_version_info_response)
    def get(self, id, version):
        version = ServicesInitializer.an_api_version_service().get_api_version(
            api_id=id, version=version
        )
        return {
            "data": version,
        }, HTTPStatus.OK


@api_version.route("/mine/<int:id>/versions/<string:version>")
class GetMyApiVersion(Resource):
    @api_version.doc("get my version")
    @api_version.response(
        HTTPStatus.OK, "Success", ApiDto.full_api_version_info_response
    )
    @role_token_required([Role.SUPPLIER])
    def get(self, id, version):
        version = ServicesInitializer.an_api_version_service().get_full_api_version(
            api_id=id,
            version=version,
            supplier_id=top_g.user.get("id"),
            role=top_g.user.get("role"),
        )
        return {
            "data": version,
        }, HTTPStatus.OK


@api_version.route("/<int:id>/versions/<string:version>/activate")
class ActivateVersion(Resource):
    @api_version.doc("activate version")
    @api_version.response(HTTPStatus.OK, "Success")
    @role_token_required([Role.SUPPLIER, Role.ADMIN])
    def patch(self, id, version):
        ServicesInitializer.an_api_version_service().activate_version(
            api_id=id,
            version=version,
            supplier_id=top_g.user.get("id"),
            role=top_g.user.get("role"),
        )
        return Response(status=HTTPStatus.OK)


@api_version.route("/<int:id>/versions/<string:version>/deactivate")
class DeactivateVersion(Resource):
    @api_version.doc("deactivate version")
    @api_version.response(HTTPStatus.OK, "Success")
    @role_token_required([Role.SUPPLIER, Role.ADMIN])
    def patch(self, id, version):
        ServicesInitializer.an_api_version_service().deactivate_version(
            api_id=id,
            version=version,
            supplier_id=top_g.user.get("id"),
            role=top_g.user.get("role"),
        )
        return Response(status=HTTPStatus.OK)


@api_subscription.route("/<int:id>/<string:plan_name>/chargily/checkout")
class CreateCheckout(Resource):
    @api_subscription.doc("create checkout")
    @api_subscription.response(
        HTTPStatus.OK, "Success", ApiDto.create_charigly_checkout_response
    )
    @api_subscription.param("redirect_url", "The redirect URL")
    @role_token_required([Role.USER])
    def post(self, id, plan_name):
        return {
            "checkout_url": ServicesInitializer.an_api_subscription_service().create_charigly_checkout(
                api_id=id,
                plan_name=plan_name,
                redirect_url=request.args.get("redirect_url"),
                user_id=top_g.user.get("id"),
            )
        }


@api_subscription.route("/subscriptions")
class GetSubscriptions(Resource):
    @api_subscription.doc("get subscriptions")
    @api_subscription.response(
        HTTPStatus.OK, "Success", ApiDto.subscriptions_list_response
    )
    @role_token_required([Role.SUPPLIER, Role.ADMIN])
    @api_subscription.param("page", "The page number")
    @api_subscription.param("per_page", "The per page number")
    @api_subscription.param("api_id", "The API ID")
    @api_subscription.param("user_id", "The user ID")
    @api_subscription.param("plan_name", "The plan name")
    @api_subscription.param("start_date", "The start date")
    @api_subscription.param("end_date", "The end date")
    @api_subscription.param("expired", "true or false")
    def get(self):
        (
            data,
            pagination,
        ) = ServicesInitializer.an_api_subscription_service().get_subscriptions(
            {**request.args, "supplier_id": top_g.user.get("id")},
            role=top_g.user.get("role"),
        )
        return {"data": data, "pagination": pagination}


@api_subscription.route("/subscriptions/mine")
class GetMySubscriptions(Resource):
    @api_subscription.doc("get my subscriptions")
    @api_subscription.response(
        HTTPStatus.OK, "Success", ApiDto.subscriptions_list_response
    )
    @role_token_required([Role.USER])
    @api_subscription.param("page", "The page number")
    @api_subscription.param("per_page", "The per page number")
    @api_subscription.param("api_id", "The API ID")
    @api_subscription.param("plan_name", "The plan name")
    @api_subscription.param("start_date", "The start date")
    @api_subscription.param("end_date", "The end date")
    @api_subscription.param("expired", "true or false")
    @api_subscription.param("supplier_id", "The supplier ID")
    def get(self):
        (
            data,
            pagination,
        ) = ServicesInitializer.an_api_subscription_service().get_subscriptions(
            {
                **request.args,
                "user_id": top_g.user.get("id"),
            },
            role=top_g.user.get("role"),
        )
        return {"data": data, "pagination": pagination}


@api_subscription.route("/subscriptions/<int:id>")
class GetSubscription(Resource):
    @api_subscription.doc("get subscription")
    @api_subscription.response(
        HTTPStatus.OK, "Success", ApiDto.subscription_info_response
    )
    @role_token_required([Role.SUPPLIER, Role.ADMIN, Role.USER])
    def get(self, id):
        return ServicesInitializer.an_api_subscription_service().get_subscription(
            subscription_id=id,
            user_id=top_g.user.get("id"),
            role=top_g.user.get("role"),
        )


@api_subscription.route("/webhook/chargily")
class ChargilyWebhook(Resource):
    @api_subscription.doc("chargily webhook")
    def post(self):
        ServicesInitializer.an_api_subscription_service().handle_chargily_webhook(
            request
        )
        return Response(status=HTTPStatus.OK)


@api_subscription.route("/<int:id>/subscriptions/statistics", doc=False)
class GetSubscriptionsRevenuePerDay(Resource):
    @api_subscription.doc("get subscriptions per day")
    @api_subscription.response(
        HTTPStatus.OK, "Success", ApiDto.subscriptions_per_day_list_response
    )
    @role_token_required([Role.SUPPLIER, Role.ADMIN])
    def get(self, id):
        data = (
            ServicesInitializer.an_api_subscription_service().get_subscriptions_per_day(
                api_id=id,
                supplier_id=top_g.user.get("id"),
                role=top_g.user.get("role"),
            )
        )
        return {"data": data}, HTTPStatus.OK


@api_subscription.route("/subscriptions/revenue/month")
class GetSubscriptionRevenuesByMonth(Resource):
    @api_subscription.doc("get total subscription revenue by month")
    @api.param("year", "The year of the subscription")
    @api_subscription.response(
        HTTPStatus.OK,
        "Success",
        ApiDto.api_total_subscription_revenue_by_month_response,
    )
    @role_token_required([Role.ADMIN])
    def get(self):
        total_revenues = ServicesInitializer.an_api_subscription_service().get_total_subscription_revenue_by_month(
            {**request.args}
        )
        return {"data": total_revenues}, HTTPStatus.OK


@api_subscription.route("/subscriptions/revenue/day")
class GetSubscriptionRevenuesByDay(Resource):
    @api_subscription.doc("get total subscription revenue by day")
    @api.param("year", "The year of the subscription")
    @api.param("month", "The month of the subscription")
    @api_subscription.response(
        HTTPStatus.OK,
        "Success",
        ApiDto.api_total_subscription_revenue_by_day_response,
    )
    @role_token_required([Role.ADMIN])
    def get(self):
        total_revenues = ServicesInitializer.an_api_subscription_service().get_total_subscription_revenue_by_day(
            {**request.args}
        )
        return {"data": total_revenues}, HTTPStatus.OK


@api_subscription.route("/subscriptions/revenue/hour")
class GetSubscriptionRevenuesByHour(Resource):
    @api_subscription.doc("get total subscription revenue by hour")
    @api.param("year", "The year of the subscription")
    @api.param("month", "The month of the subscription")
    @api.param("day", "The day of the subscription")
    @api_subscription.response(
        HTTPStatus.OK,
        "Success",
        ApiDto.api_total_subscription_revenue_by_hour_response,
    )
    @role_token_required([Role.ADMIN])
    def get(self):
        total_revenues = ServicesInitializer.an_api_subscription_service().get_total_subscription_revenue_by_hour(
            {**request.args}
        )
        return {"data": total_revenues}, HTTPStatus.OK


@api_subscription.route("/subscriptions/revenue")
class GetSubscriptionTotalRevenues(Resource):
    @api_subscription.doc("get total subscription revenue")
    @api_subscription.response(
        HTTPStatus.OK,
        "Success",
        ApiDto.apis_total_revenue_response,
    )
    @role_token_required([Role.ADMIN])
    def get(self):
        total_revenues = (
            ServicesInitializer.an_api_subscription_service().get_total_subscription_revenue()
        )
        return {"data": total_revenues}, HTTPStatus.OK


@api_subscription.route("/subscriptions/mine/revenue/month")
class GetSupplierRevenuesByMonth(Resource):
    @api_subscription.doc("get total supplier revenue by month")
    @api.param("year", "The year of the subscription")
    @api_subscription.response(
        HTTPStatus.OK,
        "Success",
        ApiDto.api_total_subscription_revenue_by_month_response,
    )
    @role_token_required([Role.SUPPLIER])
    def get(self):
        total_revenues = ServicesInitializer.an_api_subscription_service().get_total_supplier_revenue_by_month(
            supplier_id=top_g.user.get("id"), query_params=request.args
        )
        return {"data": total_revenues}, HTTPStatus.OK


@api_subscription.route("/subscriptions/mine/revenue/day")
class GetSupplierRevenuesByDay(Resource):
    @api_subscription.doc("get total supplier revenue by day")
    @api.param("year", "The year of the subscription")
    @api.param("month", "The month of the subscription")
    @api_subscription.response(
        HTTPStatus.OK,
        "Success",
        ApiDto.api_total_subscription_revenue_by_day_response,
    )
    @role_token_required([Role.SUPPLIER])
    def get(self):
        total_revenues = ServicesInitializer.an_api_subscription_service().get_total_supplier_revenue_by_day(
            supplier_id=top_g.user.get("id"), query_params=request.args
        )
        return {"data": total_revenues}, HTTPStatus.OK


@api_subscription.route("/subscriptions/mine/revenue/hour")
class GetSupplierRevenuesByHour(Resource):
    @api_subscription.doc("get total supplier revenue by hour")
    @api.param("year", "The year of the subscription")
    @api.param("month", "The month of the subscription")
    @api.param("day", "The day of the subscription")
    @api_subscription.response(
        HTTPStatus.OK,
        "Success",
        ApiDto.api_total_subscription_revenue_by_hour_response,
    )
    @role_token_required([Role.SUPPLIER])
    def get(self):
        total_revenues = ServicesInitializer.an_api_subscription_service().get_total_supplier_revenue_by_hour(
            supplier_id=top_g.user.get("id"), query_params=request.args
        )
        return {"data": total_revenues}, HTTPStatus.OK


@api_keys.route("/subscriptions/<int:id>/api-keys/create")
class CreateApiKey(Resource):
    @api_keys.doc("create api key")
    @api_keys.response(HTTPStatus.CREATED, "Success")
    @role_token_required([Role.USER])
    def post(self, id):
        ServicesInitializer.an_api_key_service().create_api_key(
            subscription_id=id, user_id=top_g.user.get("id")
        )
        return Response(status=HTTPStatus.CREATED)


@api_keys.route("/api-keys/deactivate")
class DeactivateApiKey(Resource):
    @api_keys.doc("deactivate api key")
    @api_keys.expect(ApiDto.deactivate_api_key_request, validate=True)
    @api_keys.response(HTTPStatus.OK, "Success")
    @role_token_required([Role.USER])
    def patch(self):
        ServicesInitializer.an_api_key_service().deactivate_api_key(
            user_id=top_g.user.get("id"), key=api_keys.payload["key"]
        )
        return Response(status=HTTPStatus.OK)


@api_keys.route("/api-keys/activate")
class ActivateApiKey(Resource):
    @api_keys.doc("activate api key")
    @api_keys.expect(ApiDto.activate_api_key_request, validate=True)
    @api_keys.response(HTTPStatus.OK, "Success")
    @role_token_required([Role.USER])
    def patch(self):
        ServicesInitializer.an_api_key_service().activate_api_key(
            user_id=top_g.user.get("id"), key=api_keys.payload["key"]
        )
        return Response(status=HTTPStatus.OK)


@api_keys.route("/subscriptions/<int:id>/api-keys")
class GetApiKeys(Resource):
    @api_keys.doc("get api keys")
    @api_keys.response(HTTPStatus.OK, "Success", ApiDto.api_keys_list_response)
    @role_token_required([Role.USER])
    def get(self, id):
        return {
            "data": ServicesInitializer.an_api_key_service().get_api_keys(
                subscription_id=id, user_id=top_g.user.get("id")
            )
        }, HTTPStatus.OK


@api_tests.route("/test/<int:id>/<string:version>/<path:params>")
class TestEndpoint(Resource):
    @api_tests.doc("test GET Endpoint")
    @require_authentication
    def get(self, id, version, params):
        return ServicesInitializer.an_api_tests_service().test_get(
            api_id=id, version=version, params=params
        )

    @api_tests.doc("test POST Endpoint")
    @require_authentication
    def post(self, id, version, params):
        return ServicesInitializer.an_api_tests_service().test_post(
            api_id=id, version=version, params=params, data=api_tests.payload
        )

    @api_tests.doc("Test PATCH Endpoint")
    @require_authentication
    def patch(self, id, version, params):
        return ServicesInitializer.an_api_tests_service().test_patch(
            api_id=id, version=version, params=params, data=api_tests.payload
        )

    @api_tests.doc("Test DELETE Endpoint")
    @require_authentication
    def delete(self, id, version, params):
        return ServicesInitializer.an_api_tests_service().test_delete(
            api_id=id, version=version, params=params
        )


@api_calls.route("/call/<int:id>/<string:version>/<path:params>")
class CallEndpoint(Resource):
    @api_calls.doc("Call GET Endpoint")
    def get(self, id, version, params=""):
        api_key = request.headers.get("X-itouch-key")
        return ServicesInitializer.an_api_call_service().call_get(
            api_id=id, version=version, params=params, api_key=api_key
        )

    @api_calls.doc("Call POST Endpoint")
    def post(self, id, version, params=""):
        api_key = request.headers.get("X-itouch-key")
        return ServicesInitializer.an_api_call_service().call_post(
            api_id=id,
            version=version,
            params=params,
            data=api_calls.payload,
            api_key=api_key,
            body=api_calls.payload,
        )

    @api_calls.doc("Call PATCH Endpoint")
    def patch(self, id, version, params=""):
        api_key = request.headers.get("X-itouch-key")
        return ServicesInitializer.an_api_call_service().call_patch(
            api_id=id,
            version=version,
            params=params,
            data=api_calls.payload,
            api_key=api_key,
            body=api_calls.payload,
        )

    @api_calls.doc("Call DELETE Endpoint")
    def delete(self, id, version, params=""):
        api_key = request.headers.get("X-itouch-key")
        return ServicesInitializer.an_api_call_service().call_delete(
            api_id=id, version=version, params=params, api_key=api_key
        )


@api_discussions.route("/<int:api_id>/discussions")
class Discussions(Resource):
    @api_discussions.doc("get a specific api discussions")
    @api_discussions.marshal_list_with(ApiDto.discussions_response, envelope="data")
    @api_discussions.response(HTTPStatus.OK, "Success", ApiDto.discussions_response)
    def get(self, api_id):
        return (
            ServicesInitializer.a_discussion_service().get_all_by_api_id(api_id=api_id),
            HTTPStatus.OK,
        )

    @api_discussions.doc("create a new discussion")
    @api_discussions.expect(ApiDto.create_discussion_request, validate=True)
    @api_discussions.marshal_with(
        ApiDto.discussions_response, envelope="data", code=HTTPStatus.CREATED
    )
    @require_authentication
    def post(self, api_id):
        return (
            ServicesInitializer.a_discussion_service().create_new_discussion(
                api_id, api_discussions.payload, top_g.user.get("id")
            ),
            HTTPStatus.CREATED,
        )


@api_discussions.route("/<int:api_id>/discussions/<int:discussion_id>")
class DiscussionDetails(Resource):
    @api_discussions.doc("get a specific discussion")
    @api_discussions.marshal_with(ApiDto.discussion_details_response, envelope="data")
    def get(self, discussion_id, **_):
        return (
            ServicesInitializer.a_discussion_service().get_by_id(discussion_id),
            HTTPStatus.OK,
        )

    @api_discussions.doc("delete a specific discussion")
    @api_discussions.response(HTTPStatus.OK, "Success")
    @require_authentication
    @check_delete_discussion_permission
    def delete(self, discussion_id, **_):
        ServicesInitializer.a_discussion_service().delete_discussion(discussion_id)
        return Response(status=HTTPStatus.OK)


@api_discussions.route("/<int:api_id>/discussions/<int:discussion_id>/answers")
class DiscussionAnswers(Resource):
    @api_discussions.doc("create a new discussion answer")
    @api_discussions.expect(ApiDto.create_discussion_answer_request, validate=True)
    @api_discussions.marshal_with(
        ApiDto.discussion_answer_response, envelope="data", code=HTTPStatus.CREATED
    )
    @require_authentication
    def post(self, discussion_id, **_):
        return (
            ServicesInitializer.a_discussion_service().create_new_answer(
                discussion_id, api_discussions.payload, top_g.user.get("id")
            ),
            HTTPStatus.CREATED,
        )


@api_discussions.route(
    "/<int:api_id>/discussions/<int:discussion_id>/answers/<int:answer_id>"
)
class AnswerDetails(Resource):
    @api_discussions.doc("get a specific answer")
    @api_discussions.marshal_with(ApiDto.discussion_answer_response, envelope="data")
    def get(self, answer_id, **_):
        return (
            ServicesInitializer.a_discussion_service().get_answer_by_id(answer_id),
            HTTPStatus.OK,
        )

    @api_discussions.doc("delete a specific answer")
    @api_discussions.response(HTTPStatus.OK, "Success")
    @require_authentication
    @check_delete_answer_permission
    def delete(self, answer_id, **_):
        ServicesInitializer.a_discussion_service().delete_answer(answer_id)
        return Response(status=HTTPStatus.OK)


@api_discussions.route(
    "/<int:api_id>/discussions/<int:discussion_id>/answers/<int:answer_id>/votes"
)
class Votes(Resource):
    @api_discussions.doc("vote on an answer")
    @api_discussions.expect(ApiDto.create_vote_request, validate=True)
    @api_discussions.response(HTTPStatus.NO_CONTENT, "Success")
    @require_authentication
    def post(self, answer_id, **_):
        ServicesInitializer.a_discussion_service().vote_on_answer(
            answer_id, top_g.user.get("id"), api_discussions.payload["vote"]
        )
        return Response(status=HTTPStatus.NO_CONTENT)

    @api_discussions.doc("remove vote from an answer")
    @api_discussions.response(HTTPStatus.NO_CONTENT, "Success")
    @require_authentication
    def delete(self, answer_id, **_):
        ServicesInitializer.a_discussion_service().remove_vote(
            answer_id, top_g.user.get("id")
        )
        return Response(status=HTTPStatus.NO_CONTENT)

    @api_discussions.doc(description="get user vote for answer")
    @api_discussions.marshal_with(
        ApiDto.user_vote_response, envelope="data", code=HTTPStatus.OK
    )
    @api_discussions.response(HTTPStatus.NOT_FOUND, "User haven't voted on this answer")
    @require_authentication
    def get(self, answer_id, **_):
        return (
            ServicesInitializer.a_discussion_service().get_user_vote(
                answer_id, top_g.user.get("id")
            ),
            HTTPStatus.OK,
        )

    @api_resquests.route("/<int:id>/requests")
    class GetRequests(Resource):
        @api_resquests.doc("get requests")
        @api_resquests.response(HTTPStatus.OK, "Success", ApiDto.requests_list_response)
        @role_token_required([Role.SUPPLIER])
        @api_resquests.param("page", "The page number")
        @api_resquests.param("per_page", "The per page number")
        @api_resquests.param("http_status", "The http status of the request")
        @api_resquests.param("version", "The api version")
        @api_resquests.param("start_date", "The start date")
        @api_resquests.param("end_date", "The end date")
        def get(self, id):
            (
                data,
                pagination,
            ) = ServicesInitializer.an_api_request_service().get_api_requests(
                query_params=request.args, user_id=top_g.user.get("id"), api_id=id
            )
            return {"data": data, "pagination": pagination}, HTTPStatus.OK

    @api_resquests.route("/requests/count/month", doc=False)
    class GetRequestsByMonth(Resource):
        @api_resquests.doc("get total requests by month")
        @api_resquests.response(
            HTTPStatus.OK, "Success", ApiDto.api_total_transactions_by_month_response
        )
        @role_token_required([Role.ADMIN])
        def get(self):
            total_transaction = (
                ServicesInitializer.an_api_request_service().get_total_transactions_by_month()
            )
            return {"data": total_transaction}, HTTPStatus.OK

    @api_resquests.route("/requests/count/day", doc=False)
    class GetRequestsByDay(Resource):
        @api_resquests.doc("get total requests by day")
        @api_resquests.response(
            HTTPStatus.OK, "Success", ApiDto.api_total_transactions_by_day_response
        )
        @role_token_required([Role.ADMIN])
        def get(self):
            total_transaction = (
                ServicesInitializer.an_api_request_service().get_total_transactions_by_day()
            )
            return {"data": total_transaction}, HTTPStatus.OK

    @api_resquests.route("/requests/count/hour", doc=False)
    class GetRequestsByHour(Resource):
        @api_resquests.doc("get total requests by hour")
        @api_resquests.response(
            HTTPStatus.OK, "Success", ApiDto.api_total_transactions_by_hour_response
        )
        @role_token_required([Role.ADMIN])
        def get(self):
            total_transaction = (
                ServicesInitializer.an_api_request_service().get_total_transactions_by_hour()
            )
            return {"data": total_transaction}, HTTPStatus.OK


@api_tickets.route("/<int:api_id>/tickets/create")
class CreateTicket(Resource):
    @api_tickets.doc("create ticket")
    @api_tickets.expect(ApiDto.create_ticket_request, validate=True)
    @api_tickets.response(HTTPStatus.CREATED, "success")
    @role_token_required([Role.USER])
    def post(self, api_id):
        ServicesInitializer.an_api_tickets_service().create_ticket(
            api_id, request.json, top_g.user.get("id")
        )
        return Response(status=HTTPStatus.CREATED)


@api_tickets.route("/<int:api_id>/tickets")
class GetTickets(Resource):
    @api_tickets.doc("get tickets")
    def get(self, api_id):
        tickets = ServicesInitializer.an_api_tickets_service().get_tickets(api_id)
        return {
            "data": tickets,
        }, HTTPStatus.OK


@api_tickets.route("/<int:api_id>/tickets/<int:id>")
class RespondToTicket(Resource):
    @api_tickets.doc("respond to ticket")
    @api_tickets.expect(ApiDto.respond_to_ticket_request, validate=True)
    @role_token_required([Role.SUPPLIER])
    def patch(self, api_id, id):
        ServicesInitializer.an_api_tickets_service().respond_to_ticket(
            top_g.user.get("id"), api_id, id, request.json
        )
        return Response(status=HTTPStatus.OK)
