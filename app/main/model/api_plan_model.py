from app.main import db


class ApiPlan(db.Model):  # type: ignore

    __tablename__ = "api_plan"

    api_id = db.Column(db.Integer, db.ForeignKey("api.id"), primary_key=True)
    name = db.Column(db.String, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer)
    max_requests = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    chargily_price_id = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return "<ApiPlan '{}'>".format(self.name)

    def __str__(self):
        return self.name
