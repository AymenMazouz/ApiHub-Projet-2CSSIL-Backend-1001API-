from datetime import datetime, timedelta
import math

from typing import Dict

from flask import Request
from sqlalchemy import func, extract

from app.main import db

from app.main.utils.roles import Role

from app.main.core.lib.chargily_api import ChargilyApi
from app.main.model.api_model import ApiModel
from app.main.model.api_plan_model import ApiPlan
from app.main.model.user_model import User
from app.main.model.api_subscription_model import ApiSubscription
from app.main.utils.exceptions import NotFoundError, BadRequestError


class ApiSubscriptionService:
    def __init__(self, chargily_api: ChargilyApi):
        self.chargily_api = chargily_api

    def create_charigly_checkout(
        self, api_id: str, plan_name: str, user_id: str, redirect_url: str
    ) -> str:
        api = ApiModel.query.filter_by(id=api_id).first()
        if api is None:
            raise NotFoundError(f"No API found with id: {api_id}")

        plan = ApiPlan.query.filter_by(api_id=api_id, name=plan_name).first()
        if plan is None:
            raise NotFoundError(f"No plan found with name: {plan_name}")

        price_id = plan.chargily_price_id

        if price_id is None:
            raise BadRequestError("Failed to get price id from chargily API")

        checkout_url = self.chargily_api.create_checkout(
            price_id=price_id,
            redirect_url=redirect_url,
            metadata={"api_id": api_id, "plan_name": plan_name, "user_id": user_id},
        )

        if checkout_url is None:
            raise BadRequestError("Failed to create checkout URL in chargily API")

        return checkout_url

    def handle_chargily_webhook(self, request: Request):
        signature = request.headers.get("signature")

        if signature is None:
            raise BadRequestError("No signature found in headers")

        body = request.data

        if body is None:
            raise BadRequestError("No body found in request")

        payload = body.decode("utf-8")

        if not self.chargily_api.verify_webhook_signature(payload, signature):
            raise BadRequestError("Invalid signature, STOP TRYING TO HACK US")

        event = request.json

        if event is None:
            raise BadRequestError("No JSON found in request")

        if event["type"] == "checkout.paid":
            checkout = event["data"]

            api_id = checkout["metadata"]["api_id"]
            plan_name = checkout["metadata"]["plan_name"]
            user_id = checkout["metadata"]["user_id"]
            amount = checkout["amount"]

            api = ApiModel.query.filter_by(id=api_id).first()
            if api is None:
                raise NotFoundError(f"No API found with id: {api_id}")

            plan = ApiPlan.query.filter_by(api_id=api_id, name=plan_name).first()
            if plan is None:
                raise NotFoundError(f"No plan found with name: {plan_name}")

            duration = plan.duration

            subscription = ApiSubscription(
                api_id=api_id,
                plan_name=plan_name,
                user_id=user_id,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(seconds=duration),
                max_requests=plan.max_requests,
                status="active",
                price=amount,
            )

            db.session.add(subscription)
            db.session.commit()

    def get_subscriptions(self, query_params: Dict, role: str):
        page = int(query_params.get("page", 1))
        per_page = int(query_params.get("per_page", 10))
        api_id = query_params.get("api_id")
        plan_name = query_params.get("plan_name")
        user_id = query_params.get("user_id")
        start_date = query_params.get("start_date")
        end_date = query_params.get("end_date")
        expired = query_params.get("expired")
        supplier_id = query_params.get("supplier_id")

        query = (
            db.session.query(ApiSubscription, ApiModel, User)
            .join(ApiModel, ApiSubscription.api_id == ApiModel.id)
            .join(
                User,
                ApiSubscription.user_id == User.id,
            )
        )

        if api_id is not None:
            query = query.filter(ApiModel.id == api_id)

            if plan_name is not None:
                query = query.filter(ApiSubscription.plan_name == plan_name)

        if user_id is not None:
            query = query.filter(User.id == user_id)

        if start_date is not None:
            query = query.filter(ApiSubscription.start_date >= start_date)

        if end_date is not None:
            query = query.filter(ApiSubscription.end_date <= end_date)

        if expired is not None:
            if expired == "true":
                query = query.filter(ApiSubscription.end_date < datetime.now())
            else:
                query = query.filter(ApiSubscription.end_date >= datetime.now())

        if role == Role.SUPPLIER:
            if supplier_id is None:
                raise BadRequestError("Supplier ID is required for supplier role")
            query = query.filter(ApiModel.supplier_id == supplier_id)

        query = query.limit(per_page).offset((page - 1) * per_page)

        total = query.count()
        total_pages = math.ceil(total / per_page)

        return [
            {
                "id": item.ApiSubscription.id,
                "api_id": item.ApiModel.id,
                "api": {
                    "id": item.ApiModel.id,
                    "name": item.ApiModel.name,
                    "supplier_id": item.ApiModel.supplier_id,
                },
                "api_plan": item.ApiSubscription.plan_name,
                "user_id": item.User.id,
                "user": {
                    "id": item.User.id,
                    "firstname": item.User.firstname,
                    "lastname": item.User.lastname,
                },
                "start_date": item.ApiSubscription.start_date.isoformat(),
                "end_date": item.ApiSubscription.end_date.isoformat(),
                "remaining_requests": item.ApiSubscription.max_requests,
                "status": item.ApiSubscription.status,
                "expired": item.ApiSubscription.end_date < datetime.now(),
                "price": item.ApiSubscription.price,
            }
            for item in query.all()
        ], {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        }

    def get_subscription(self, subscription_id: str, user_id: str, role: str):
        query = (
            db.session.query(ApiSubscription, ApiModel, User)
            .join(ApiModel, ApiSubscription.api_id == ApiModel.id)
            .join(
                User,
                ApiSubscription.user_id == User.id,
            )
        )

        query = query.filter(ApiSubscription.id == subscription_id)

        item = query.first()

        if item is None:
            raise NotFoundError(f"No subscription found with id: {subscription_id}")

        if role == Role.SUPPLIER and item.ApiModel.supplier_id != user_id:
            raise BadRequestError("You are not allowed to view this subscription")

        if role == Role.USER and item.User.id != user_id:
            raise BadRequestError("You are not allowed to view this subscription")

        return {
            "id": item.ApiSubscription.id,
            "api_id": item.ApiModel.id,
            "api": {
                "id": item.ApiModel.id,
                "name": item.ApiModel.name,
                "supplier_id": item.ApiModel.supplier_id,
            },
            "api_plan": item.ApiSubscription.plan_name,
            "user_id": item.User.id,
            "user": {
                "id": item.User.id,
                "firstname": item.User.firstname,
                "lastname": item.User.lastname,
            },
            "start_date": item.ApiSubscription.start_date.isoformat(),
            "end_date": item.ApiSubscription.end_date.isoformat(),
            "remaining_requests": item.ApiSubscription.max_requests,
            "status": item.ApiSubscription.status,
            "expired": item.ApiSubscription.end_date < datetime.now(),
            "price": item.ApiSubscription.price,
        }

    def get_subscriptions_per_day(self, api_id: int, role: str, supplier_id: str):
        api = ApiModel.query.filter_by(id=api_id).first()

        if api is None:
            raise NotFoundError("No API found with id: {}".format(api_id))

        if role == Role.SUPPLIER and api.supplier_id != supplier_id:
            raise BadRequestError("You are not allowed to view this informations")

        # Query to group subscriptions by start_date and count the number of subscriptions per day
        subscriptions_per_day = (
            db.session.query(
                func.date(ApiSubscription.start_date), func.count(ApiSubscription.id)
            )
            .filter(ApiSubscription.api_id == api_id)
            .group_by(func.date(ApiSubscription.start_date))
            .all()
        )

        # Construct a list of dictionaries containing date and count
        subscriptions_per_day_list = []
        for date, count in subscriptions_per_day:
            subscriptions_per_day_list.append({"date": date, "count": count})

        return {"subscriptions_per_day_list": subscriptions_per_day_list}

    def get_total_subscription_revenue_by_month(self, query_params: Dict):
        current_date = datetime.now()
        year = int(query_params.get("year", current_date.year))
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)

        # Query to calculate total subscription revenue by month
        total_revenue = (
            db.session.query(
                extract("year", ApiSubscription.start_date).label("year"),
                extract("month", ApiSubscription.start_date).label("month"),
                func.sum(ApiSubscription.price).label("total_revenue"),
            )
            .filter(ApiSubscription.start_date >= start_date)
            .filter(ApiSubscription.start_date <= end_date)
            .group_by(
                extract("year", ApiSubscription.start_date),
                extract("month", ApiSubscription.start_date),
            )
            .order_by("year", "month")
            .all()
        )
        return [
            {
                "year": year,
                "month": month,
                "total_revenues": revenues,
            }
            for year, month, revenues in total_revenue
        ]

    def get_total_subscription_revenue_by_day(self, query_params: Dict):
        current_date = datetime.now()
        year = int(query_params.get("year", current_date.year))
        month = int(query_params.get("month", current_date.month))
        start_date = datetime(year, month, 1)
        # Calculate the first day of the next month
        next_month = month % 12 + 1
        next_year = year + (month // 12)
        end_date = datetime(next_year, next_month, 1) - timedelta(days=1)
        # Query to calculate total subscription revenue by day
        total_revenue = (
            db.session.query(
                extract("year", ApiSubscription.start_date).label("year"),
                extract("month", ApiSubscription.start_date).label("month"),
                extract("day", ApiSubscription.start_date).label("day"),
                func.sum(ApiSubscription.price).label("total_revenue"),
            )
            .filter(ApiSubscription.start_date >= start_date)
            .filter(ApiSubscription.start_date <= end_date)
            .group_by(
                extract("year", ApiSubscription.start_date),
                extract("month", ApiSubscription.start_date),
                extract("day", ApiSubscription.start_date),
            )
            .order_by("year", "month", "day")
            .all()
        )

        return [
            {
                "year": year,
                "month": month,
                "day": day,
                "total_revenues": revenues,
            }
            for year, month, day, revenues in total_revenue
        ]

    def get_total_subscription_revenue_by_hour(self, query_params: Dict):
        current_date = datetime.now()
        year = int(query_params.get("year", current_date.year))
        month = int(query_params.get("month", current_date.month))
        day = int(query_params.get("day", current_date.day))
        start_date = datetime(year, month, day)
        end_date = start_date.replace(hour=23, minute=59, second=59)
        # Query to calculate total subscription revenue by hour
        total_revenue = (
            db.session.query(
                extract("year", ApiSubscription.start_date).label("year"),
                extract("month", ApiSubscription.start_date).label("month"),
                extract("day", ApiSubscription.start_date).label("day"),
                extract("hour", ApiSubscription.start_date).label("hour"),
                func.sum(ApiSubscription.price).label("total_revenue"),
            )
            .filter(ApiSubscription.start_date >= start_date)
            .filter(ApiSubscription.start_date <= end_date)
            .group_by(
                extract("year", ApiSubscription.start_date),
                extract("month", ApiSubscription.start_date),
                extract("day", ApiSubscription.start_date),
                extract("hour", ApiSubscription.start_date),
            )
            .order_by("year", "month", "day", "hour")
            .all()
        )

        return [
            {
                "year": year,
                "month": month,
                "day": day,
                "hour": hour,
                "total_revenues": revenues,
            }
            for year, month, day, hour, revenues in total_revenue
        ]

    def get_total_subscription_revenue(self):
        # Query to calculate total subscription revenue
        total_revenue = db.session.query(func.sum(ApiSubscription.price)).scalar() or 0
        return {"total_revenue": total_revenue}

    def get_total_supplier_revenue_by_month(self, supplier_id, query_params: Dict):
        current_date = datetime.now()
        year = int(query_params.get("year", current_date.year))
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)

        # Query to calculate total subscription revenue by month
        total_revenue = (
            db.session.query(
                extract("year", ApiSubscription.start_date).label("year"),
                extract("month", ApiSubscription.start_date).label("month"),
                func.sum(ApiSubscription.price).label("total_revenue"),
            )
            .join(ApiModel, ApiSubscription.api_id == ApiModel.id)
            .filter(ApiSubscription.start_date >= start_date)
            .filter(ApiSubscription.start_date <= end_date)
            .filter(ApiModel.supplier_id == supplier_id)
            .group_by(
                extract("year", ApiSubscription.start_date),
                extract("month", ApiSubscription.start_date),
            )
            .order_by("year", "month")
            .all()
        )
        return [
            {
                "year": year,
                "month": month,
                "total_revenues": revenues,
            }
            for year, month, revenues in total_revenue
        ]

    def get_total_supplier_revenue_by_day(self, supplier_id, query_params: Dict):
        current_date = datetime.now()
        year = int(query_params.get("year", current_date.year))
        month = int(query_params.get("month", current_date.month))
        start_date = datetime(year, month, 1)
        # Calculate the first day of the next month
        next_month = month % 12 + 1
        next_year = year + (month // 12)
        end_date = datetime(next_year, next_month, 1) - timedelta(days=1)
        # Query to calculate total subscription revenue by day
        total_revenue = (
            db.session.query(
                extract("year", ApiSubscription.start_date).label("year"),
                extract("month", ApiSubscription.start_date).label("month"),
                extract("day", ApiSubscription.start_date).label("day"),
                func.sum(ApiSubscription.price).label("total_revenue"),
            )
            .join(ApiModel, ApiSubscription.api_id == ApiModel.id)
            .filter(ApiSubscription.start_date >= start_date)
            .filter(ApiSubscription.start_date <= end_date)
            .filter(ApiModel.supplier_id == supplier_id)
            .group_by(
                extract("year", ApiSubscription.start_date),
                extract("month", ApiSubscription.start_date),
                extract("day", ApiSubscription.start_date),
            )
            .order_by("year", "month", "day")
            .all()
        )

        return [
            {
                "year": year,
                "month": month,
                "day": day,
                "total_revenues": revenues,
            }
            for year, month, day, revenues in total_revenue
        ]

    def get_total_supplier_revenue_by_hour(self, supplier_id, query_params: Dict):
        current_date = datetime.now()
        year = int(query_params.get("year", current_date.year))
        month = int(query_params.get("month", current_date.month))
        day = int(query_params.get("day", current_date.day))
        start_date = datetime(year, month, day)
        end_date = start_date.replace(hour=23, minute=59, second=59)
        # Query to calculate total subscription revenue by hour
        total_revenue = (
            db.session.query(
                extract("year", ApiSubscription.start_date).label("year"),
                extract("month", ApiSubscription.start_date).label("month"),
                extract("day", ApiSubscription.start_date).label("day"),
                extract("hour", ApiSubscription.start_date).label("hour"),
                func.sum(ApiSubscription.price).label("total_revenue"),
            )
            .join(ApiModel, ApiSubscription.api_id == ApiModel.id)
            .filter(ApiSubscription.start_date >= start_date)
            .filter(ApiSubscription.start_date <= end_date)
            .filter(ApiModel.supplier_id == supplier_id)
            .group_by(
                extract("year", ApiSubscription.start_date),
                extract("month", ApiSubscription.start_date),
                extract("day", ApiSubscription.start_date),
                extract("hour", ApiSubscription.start_date),
            )
            .order_by("year", "month", "day", "hour")
            .all()
        )

        return [
            {
                "year": year,
                "month": month,
                "day": day,
                "hour": hour,
                "total_revenues": revenues,
            }
            for year, month, day, hour, revenues in total_revenue
        ]
