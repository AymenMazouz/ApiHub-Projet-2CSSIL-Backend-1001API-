from datetime import datetime
from uuid import uuid4
from app.main.model.api_subscription_model import ApiSubscription
from app.main.model.api_key_model import ApiKey
from app.main.utils.exceptions import BadRequestError
from app.main.utils.exceptions import NotFoundError

from app.main import db


class ApiKeyService:

    def create_api_key(self, subscription_id: int, user_id: int):
        subscription = ApiSubscription.query.filter_by(
            id=subscription_id, user_id=user_id
        ).first()

        if subscription is None:
            raise NotFoundError(f"No subscription found with id: {subscription_id}")

        if subscription.max_requests <= 0:
            raise BadRequestError(
                "Subscription has no requests left, Please Renew Subscription"
            )

        is_active = subscription.status == "active"
        if not is_active:
            raise BadRequestError("Subscription is not active")

        expired = subscription.end_date < datetime.now()

        if expired:
            raise BadRequestError("Subscription has expired")

        key = f"itouch-{uuid4()}"

        new_api_key = ApiKey(
            key=key,
            subscription_id=subscription_id,
        )

        db.session.add(new_api_key)
        db.session.commit()

    def get_api_keys(self, subscription_id: int, user_id: int):
        subscription = ApiSubscription.query.filter_by(
            id=subscription_id, user_id=user_id
        ).first()

        if subscription is None:
            raise NotFoundError(f"No subscription found with id: {subscription_id}")

        api_keys = ApiKey.query.filter_by(subscription_id=subscription_id).all()

        return [
            {
                "key": api_key.key,
                "subscription_id": api_key.subscription_id,
                "status": api_key.status,
                "created_at": api_key.created_at.isoformat(),
            }
            for api_key in api_keys
        ]

    def deactivate_api_key(self, user_id: str, key: str):
        api_key = ApiKey.query.filter_by(key=key).first()

        if api_key is None:
            raise NotFoundError(f"No api key found with key: {key}")

        subscription = ApiSubscription.query.filter_by(
            id=api_key.subscription_id
        ).first()

        if subscription is None:
            raise NotFoundError("No subscription for this api key")

        if subscription.user_id != user_id:
            raise BadRequestError("User does not own this api key")

        api_key.status = "inactive"
        db.session.commit()

    def activate_api_key(self, user_id: str, key: str):
        api_key = ApiKey.query.filter_by(key=key).first()

        if api_key is None:
            raise NotFoundError(f"No api key found with key: {key}")

        subscription = ApiSubscription.query.filter_by(
            id=api_key.subscription_id
        ).first()

        if subscription is None:
            raise NotFoundError("No subscription for this api key")

        if subscription.user_id != user_id:
            raise BadRequestError("User does not own this api key")

        api_key.status = "active"
        db.session.commit()
