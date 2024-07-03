from app.main import db


class ApiKey(db.Model):  # type: ignore

    __tablename__ = "api_key"

    key = db.Column(db.String, primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey("api_subscription.id"))
    status = db.Column(db.String, nullable=False, default="active")
    created_at = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )

    def __repr__(self):
        return "<ApiKey '{}'>".format(self.key)

    def __str__(self):
        return self.key
