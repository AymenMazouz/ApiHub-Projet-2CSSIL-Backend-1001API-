from typing import Callable, List
from functools import wraps
from flask import request, g
from app.main.model.user_model import User
from app.main.utils.exceptions import BadRequestError


def require_authentication(f: Callable) -> Callable:
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_token = request.headers.get("Authorization")

        if not auth_token:
            raise BadRequestError("Token is missing.")

        resp = User.decode_auth_token(auth_token)

        if isinstance(resp, str):
            raise BadRequestError("Invalid token. Please log in again.")

        user = User.query.filter_by(id=resp).first()

        if not user:
            raise BadRequestError("User does not exist.")

        g.user = {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "status": user.status,
        }
        return f(*args, **kwargs)

    return decorated


def role_token_required(allowed_roles: List[str]) -> Callable:
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_token = request.headers.get("Authorization")

            if not auth_token:
                raise BadRequestError("Token is missing.")

            resp = User.decode_auth_token(auth_token)

            if isinstance(resp, str):
                raise BadRequestError("Invalid token. Please log in again.")

            user = User.query.filter_by(id=resp).first()

            if not user:
                raise BadRequestError("User does not exist.")

            if user.role not in allowed_roles:
                raise BadRequestError("Unauthorized access.")

            if not user.check_status("active"):
                raise BadRequestError("User is not active.")

            g.user = {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "status": user.status,
            }

            return f(*args, **kwargs)

        return decorated

    return decorator
