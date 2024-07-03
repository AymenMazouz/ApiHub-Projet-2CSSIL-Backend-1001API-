from app.main import db


class ApiRequest(db.Model):  # type: ignore

    __tablename__ = "api_request"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    api_id = db.Column(db.Integer, db.ForeignKey("api_version.api_id"))
    api_version = db.Column(
        db.String,
        db.ForeignKey("api_version.version"),
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    api_key = db.Column(db.String, db.ForeignKey("api_key.key"))
    subscription_id = db.Column(db.Integer, db.ForeignKey("api_subscription.id"))
    request_url = db.Column(db.String, nullable=False)
    request_method = db.Column(db.String, nullable=False)
    request_body = db.Column(db.String, nullable=False)
    response_body = db.Column(db.String, nullable=False)
    request_at = db.Column(db.DateTime, nullable=False)
    response_at = db.Column(db.DateTime, nullable=False)
    response_time = db.Column(db.Integer, nullable=False)
    http_status = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<ApiRequest '{}'>".format(self.id)

    def __str__(self):
        return self.id
