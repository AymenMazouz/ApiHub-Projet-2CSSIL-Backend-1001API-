import os
import datetime
import jwt
from typing import Union

from app.main import db, flask_bcrypt
from app.main.config import key

from app.main.utils.roles import Role


class User(db.Model):  # type: ignore

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(60))
    lastname = db.Column(db.String(60))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime(), server_default=db.func.now(), server_onupdate=db.func.now()
    )
    # role can be user or admin or supplier
    role = db.Column(db.String(20), default="user")
    # status can be pending, active, suspended, or deleted
    status = db.Column(db.String(20), default="active")
    bio = db.Column(db.String(1024), default="", nullable=True)
    phone_number = db.Column(db.String(20), default="", nullable=True)

    def __init__(
        self, firstname: str, lastname: str, email: str, password: str, role=None
    ):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password_hash = flask_bcrypt.generate_password_hash(password).decode(
            "utf-8"
        )
        if role is not None:  # Check if role is provided during instantiation
            self.role = role

    def check_password(self, password: str) -> bool:
        return flask_bcrypt.check_password_hash(self.password_hash, password)

    def check_role(self, role: str) -> bool:
        return self.role == role

    def check_status(self, status: str) -> bool:
        return self.status == status

    @staticmethod
    def encode_auth_token(user_id: int):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                "exp": datetime.datetime.now(datetime.UTC)
                + datetime.timedelta(days=1, seconds=5),
                "iat": datetime.datetime.now(datetime.UTC),
                "sub": user_id,
            }
            return jwt.encode(payload, key, algorithm="HS256")
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token: str) -> Union[str, int]:
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, key, algorithms=["HS256"])
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            return "Signature expired. Please log in again."
        except jwt.InvalidTokenError:
            return "Invalid token. Please log in again."

    @staticmethod
    def create_default_admin():
        user = User.query.filter_by(
            email=os.getenv("DEFAULT_ADMIN_EMAIL", "admin@itouch.com")
        ).first()

        if user is not None:
            return

        default_admin = User(
            email=os.getenv("DEFAULT_ADMIN_EMAIL", "admin@itouch.com"),
            password=os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123"),
            firstname="Admin",
            lastname="User",
            role=Role.ADMIN,
        )

        db.session.add(default_admin)
        db.session.commit()

    def __repr__(self):
        return "<User '{}'>".format(self.email)
