from app.main import db


class ApiModel(db.Model):  # type: ignore

    __tablename__ = "api"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    category_id = db.Column(
        db.Integer, db.ForeignKey("api_category.id"), nullable=False
    )
    supplier_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime(), server_default=db.func.now(), server_onupdate=db.func.now()
    )
    status = db.Column(db.String(255), nullable=False, default="active")
    chargily_product_id = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return "<Api '{}'>".format(self.name)
