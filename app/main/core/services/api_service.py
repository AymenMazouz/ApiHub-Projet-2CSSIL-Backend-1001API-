import math
from typing import Dict
from app.main.model.api_category_model import ApiCategory
from app.main.model.api_model import ApiModel
from app.main.model.api_version_endpoint_model import ApiVersionEndpoint
from app.main.model.api_request_model import ApiRequest
from app.main.model.api_subscription_model import ApiSubscription
from app.main.model.api_plan_model import ApiPlan
from app.main.model.user_model import User
from app.main import db
from app.main.utils.exceptions import NotFoundError, BadRequestError
from app.main.core.lib.media_manager import MediaManager
from app.main.core.lib.chargily_api import ChargilyApi
from app.main.utils.roles import Role
from sqlalchemy import func
from datetime import datetime, timedelta


class ApiService:

    def __init__(self, media_manager: MediaManager, chargily_api: ChargilyApi):
        self.media_manager = media_manager
        self.chargily_api = chargily_api

    def create_api(self, data: Dict, user_id: str):
        if (
            ApiCategory.query.filter_by(id=data.get("category_id", None)).first()
            is None
        ):
            raise NotFoundError(
                "No API Category found with id: {}".format(
                    data.get("category_id", None)
                )
            )

        ApiService.__validate_plans(self, data.get("plans", []))

        new_api = ApiModel(
            name=data.get("name", None),
            description=data.get("description", None),
            category_id=data.get("category_id", None),
            supplier_id=user_id,
        )

        db.session.add(new_api)
        db.session.commit()

        product_id = self.chargily_api.create_product(new_api.name, new_api.description)

        if product_id is None:
            db.session.delete(new_api)
            db.session.commit()
            raise BadRequestError("Failed to create product in chargily API")

        new_api.chargily_product_id = product_id
        db.session.commit()

        for plan in data.get("plans", []):
            new_plan = ApiPlan(
                name=plan.get("name", None),
                price=plan.get("price", None),
                description=plan.get("description", None),
                max_requests=plan.get("max_requests", None),
                duration=plan.get("duration", None),
                api_id=new_api.id,
            )
            db.session.add(new_plan)
            price_id = self.chargily_api.create_price(
                product_id, plan.get("price", None)
            )

            if price_id is None:
                db.session.rollback()
                db.session.delete(new_api)
                db.session.commit()
                raise BadRequestError("Failed to create price in chargily API")

            new_plan.chargily_price_id = price_id

        db.session.commit()

    def __validate_plans(self, plans: Dict):
        names = []
        for plan in plans:
            if plan.get("name") in names:
                raise BadRequestError(
                    "Duplicate plan name found: {}".format(plan.get("name"))
                )
            if plan.get("price") < 0:
                raise BadRequestError("Price cannot be negative")
            if plan.get("max_requests") < 0:
                raise BadRequestError("Max requests cannot be negative")
            if plan.get("duration") < 0:
                raise BadRequestError("Duration cannot be negative")
            names.append(plan.get("name"))

    def get_apis(self, query_params: Dict):
        page = int(query_params.get("page", 1))
        per_page = int(query_params.get("per_page", 10))
        status = query_params.get("status", None)
        category_ids = query_params.get("categoryIds", None)
        supplier_id = query_params.get("supplierId", None)
        search = query_params.get("search", None)

        query = (
            db.session.query(ApiModel, User, ApiCategory)
            .join(User, ApiModel.supplier_id == User.id)
            .join(ApiCategory, ApiModel.category_id == ApiCategory.id)
        )

        if status is not None:
            query = query.filter(ApiModel.status == status)

        if category_ids:
            category_ids = [int(category_id) for category_id in category_ids.split(",")]
            query = query.filter(ApiModel.category_id.in_(category_ids))

        if supplier_id is not None:
            query = query.filter(ApiModel.supplier_id == supplier_id)

        if search is not None:
            query = query.filter(ApiModel.name.ilike("%{}%".format(search)))

        total = query.count()

        pagination = {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": math.ceil(total / per_page),
        }

        query = query.limit(per_page).offset((page - 1) * per_page)

        apis = query.all()

        result = []
        for api, user, category in apis:
            api_dict = {
                "id": api.id,
                "name": api.name,
                "description": api.description,
                "category_id": api.category_id,
                "category": {
                    "id": category.id,
                    "name": category.name,
                },
                "supplier_id": api.supplier_id,
                "supplier": {
                    "id": user.id,
                    "firstname": user.firstname,
                    "lastname": user.lastname,
                },
                "status": api.status,
                "created_at": api.created_at.isoformat(),
                "updated_at": api.updated_at.isoformat(),
                "image": self.media_manager.get_media_url_by_id(
                    api.id
                ),  # TODO: this will be api.image_id
            }
            result.append(api_dict)

        return result, pagination

    def update_api(self, api_id, supplier_id, data):
        api = ApiModel.query.filter_by(id=api_id).first()
        if api is None:
            raise NotFoundError("No API found with id: {}".format(api_id))

        if api.supplier_id != supplier_id:
            raise BadRequestError("You are not the owner of the API")

        if data.get("category_id", None) is not None:
            if (
                ApiCategory.query.filter_by(id=data.get("category_id", None)).first()
                is None
            ):
                raise NotFoundError(
                    "No API Category found with id: {}".format(
                        data.get("category_id", None)
                    )
                )
            api.category_id = data.get("category_id", None)

        if data.get("name", None) is not None:
            api.name = data.get("name", None)

        if data.get("description", None) is not None:
            api.description = data.get("description", None)

        db.session.commit()

    def get_api_by_id(self, api_id):
        query = (
            db.session.query(ApiModel, User, ApiCategory)
            .join(User, ApiModel.supplier_id == User.id)
            .join(ApiCategory, ApiModel.category_id == ApiCategory.id)
        )

        api = query.filter(ApiModel.id == api_id).first()

        if api is None:
            raise NotFoundError("No API found with id: {}".format(api_id))

        api, user, category = api

        plans = ApiPlan.query.filter_by(api_id=api.id).all()

        average_response_time = (
            db.session.query(func.avg(ApiRequest.response_time))
            .filter(ApiRequest.api_id == api_id)
            .scalar()
        )

        api_dict = {
            "id": api.id,
            "name": api.name,
            "description": api.description,
            "status": api.status,
            "average_response_time": average_response_time,
            "category_id": api.category_id,
            "category": {
                "id": category.id,
                "name": category.name,
            },
            "supplier_id": api.supplier_id,
            "supplier": {
                "id": user.id,
                "firstname": user.firstname,
                "lastname": user.lastname,
            },
            "created_at": api.created_at.isoformat(),
            "updated_at": api.updated_at.isoformat(),
            "image": self.media_manager.get_media_url_by_id(api.id),
            "plans": [
                {
                    "name": plan.name,
                    "description": plan.description,
                    "price": plan.price,
                    "max_requests": plan.max_requests,
                    "duration": plan.duration,
                }
                for plan in plans
            ],
        }

        return api_dict

    def activate_api(self, api_id: int, user_id: int, role: str):
        api = ApiModel.query.filter_by(id=api_id).first()
        if api is None:
            raise NotFoundError("No API found with id: {}".format(api_id))

        if role == Role.SUPPLIER and api.supplier_id != user_id:
            raise BadRequestError("You are not the owner of the API")

        api.status = "active"

        db.session.commit()

    def deactivate_api(self, api_id: int, user_id: int, role: str):
        api = ApiModel.query.filter_by(id=api_id).first()
        if api is None:
            raise NotFoundError("No API found with id: {}".format(api_id))

        if role == Role.SUPPLIER and api.supplier_id != user_id:
            raise BadRequestError("You are not the owner of the API")

        api.status = "inactive"

        db.session.commit()

    def get_apis_count(self, supplier_id):

        num_apis = (
            db.session.query(func.count(ApiModel.id))
            .filter(ApiModel.supplier_id == supplier_id)
            .scalar()
        )

        return {
            "apis_number": num_apis,
        }

    def get_users_count(self, supplier_id):
        current_date = datetime.now()

        query = (
            db.session.query(ApiModel, ApiSubscription)
            .join(ApiSubscription, ApiModel.id == ApiSubscription.api_id)
            .filter(ApiModel.supplier_id == supplier_id)
            .filter(ApiSubscription.status == "active")
            .filter(ApiSubscription.end_date > current_date)
            .filter(ApiSubscription.max_requests > 0)
        )

        num_users = query.distinct(ApiSubscription.user_id).count()

        return {
            "users_number": num_users,
        }

    def get_active_subscriptions_count(self, supplier_id):

        total_revenue = (
            db.session.query(func.sum(ApiSubscription.price))
            .join(ApiModel, ApiSubscription.api_id == ApiModel.id)
            .filter(ApiModel.supplier_id == supplier_id)
            .scalar()
            or 0
        )

        return {
            "total_revenue": total_revenue,
        }

    def get_api_monthly_subscribers(self, query_params: Dict, api_id):
        current_date = datetime.now()
        year = int(query_params.get("year", current_date.year))
        month = int(query_params.get("month", current_date.month))
        start_date = datetime(year, month, 1)
        # Calculate the first day of the next month
        next_month = month % 12 + 1
        next_year = year + (month // 12)
        end_date = datetime(next_year, next_month, 1) - timedelta(days=1)

        subscribers = (
            db.session.query(ApiSubscription.user_id)
            .filter(
                ApiSubscription.api_id == api_id,
                ApiSubscription.start_date <= end_date,
                ApiSubscription.end_date >= start_date,
            )
            .distinct()
            .count()
        )

        return {
            "monthly_subscribers": subscribers,
        }

    def get_endpoints_count(self, api_id):

        endpoints = (
            db.session.query(ApiVersionEndpoint.id)
            .filter(
                ApiVersionEndpoint.api_id == api_id,
            )
            .count()
        )

        return {
            "endpoints_number": endpoints,
        }

    def get_api_service_level(self, api_id):

        query = db.session.query(ApiRequest.id).filter(
            ApiRequest.api_id == api_id,
        )
        total_requests = query.count()
        successful_requests = query.filter(
            ApiRequest.http_status >= 200, ApiRequest.http_status < 300
        ).count()

        if total_requests > 0:
            service_level = (successful_requests / total_requests) * 100
        else:
            service_level = 0

        return {
            "service_level": service_level,
        }

    def get_api_popularity(self, api_id):
        current_date = datetime.now()

        api_users = (
            db.session.query(ApiModel, ApiSubscription)
            .join(ApiSubscription, ApiModel.id == ApiSubscription.api_id)
            .filter(ApiModel.id == api_id)
            .filter(ApiSubscription.status == "active")
            .filter(ApiSubscription.end_date > current_date)
            .filter(ApiSubscription.max_requests > 0)
            .distinct()
            .count()
        )

        total_users = (
            db.session.query(func.count(User.id))
            .filter(User.role == Role.USER)
            .scalar()
        )

        if total_users > 0:
            ratio = api_users / total_users
            # Scale the ratio to a value between 1 and 10
            popularity = min(max(ratio * 10, 1), 10)
        else:
            popularity = 0

        return {
            "popularity": popularity,
        }

    def get_api_monthly_revenue(self, query_params: Dict, api_id):
        current_date = datetime.now()
        year = int(query_params.get("year", current_date.year))
        month = int(query_params.get("month", current_date.month))
        start_date = datetime(year, month, 1)
        # Calculate the first day of the next month
        next_month = month % 12 + 1
        next_year = year + (month // 12)
        end_date = datetime(next_year, next_month, 1) - timedelta(days=1)
        # Query to sum up the prices of active subscriptions for the API within the specified period
        total_revenue = (
            db.session.query(func.sum(ApiSubscription.price))
            .filter(ApiSubscription.api_id == api_id)
            .filter(ApiSubscription.status == "active")
            .filter(ApiSubscription.start_date <= end_date)
            .filter(ApiSubscription.end_date >= start_date)
            .scalar()
            or 0  # Return 0 if there are no active subscriptions
        )

        return {"total_revenue": total_revenue}

    def get_api_average_successfully_response_time(self, api_id):
        # Query to get the total time responses and the number of requests passed successfully.
        result = (
            db.session.query(
                func.sum(ApiRequest.response_time),  # Total time responses
                func.count(ApiRequest.id),  # Number of requests
            )
            .filter(ApiRequest.api_id == api_id)
            .filter(ApiRequest.http_status >= 200)
            .filter(ApiRequest.http_status < 300)
            .first()  # Retrieve the first result tuple
        )

        total_time_responses, num_requests = result or (
            0,
            0,
        )  # Set default values 0 if result is None

        # Calculate average time
        if num_requests > 0:
            average_time = total_time_responses / num_requests
        else:
            average_time = 0

        return {"average_successfully_response_time": average_time}

    def get_total_apis_count(self):

        total_apis = db.session.query(func.count(ApiModel.id)).scalar()

        return {
            "total_apis_count": total_apis,
        }
