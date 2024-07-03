from app.main import db


class ApiSubscription(db.Model):  # type: ignore

    __tablename__ = "api_subscription"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    api_id = db.Column(db.Integer, db.ForeignKey("api.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    plan_name = db.Column(db.String, db.ForeignKey("api_plan.name"))
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    max_requests = db.Column(db.Integer)
    status = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=True, default=0.0)

    def __repr__(self):
        return "<ApiSubscription '{}'>".format(self.plan_name)

    def __str__(self):
        return self.plan_name
