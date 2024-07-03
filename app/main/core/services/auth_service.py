from typing import Dict
from app.main.model.user_model import User
from app.main import db
from app.main.utils.exceptions import NotFoundError, BadRequestError
from app.main.utils.validators import is_email_valid


class AuthService:

    def login(self, data: Dict):
        email = data.get("email")
        password = data.get("password")

        user = User.query.filter_by(email=email).first()

        if user is None:
            raise NotFoundError("User does not exist")

        if not user.check_password(password):
            raise BadRequestError("email or password does not match.")

        if not user.check_status("active"):
            raise BadRequestError("User is not active.")

        auth_token = User.encode_auth_token(user.id)

        return auth_token

    def register(self, data: Dict) -> int:
        email = data.get("email", "")
        password = data.get("password", "")
        firstname = data.get("firstname", "")
        lastname = data.get("lastname", "")

        user = User.query.filter_by(email=email).first()
        if user:
            raise BadRequestError("User already exists. Please Log in.")

        if not is_email_valid(email):
            raise BadRequestError("Invalid email format")

        new_user = User(
            email=email, password=password, firstname=firstname, lastname=lastname
        )

        db.session.add(new_user)
        db.session.commit()

        return new_user.id
