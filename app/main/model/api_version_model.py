from app.main import db


class ApiVersion(db.Model):  # type: ignore
    __tablename__ = "api_version"

    version = db.Column(db.String, primary_key=True)
    api_id = db.Column(db.Integer, db.ForeignKey("api.id"), primary_key=True)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime(), server_default=db.func.now(), server_onupdate=db.func.now()
    )
    base_url = db.Column(db.String(255), nullable=False)
    # status can be pending, active, suspended, or deleted
    status = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return "<ApiVersion '{}'>".format(self.version)

    def __str__(self):
        return self.version
