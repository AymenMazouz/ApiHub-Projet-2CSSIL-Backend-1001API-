from app.main import db


class ApiVersionHeader(db.Model):  # type: ignore
    __tablename__ = "api_version_header"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    api_id = db.Column(db.Integer, db.ForeignKey("api_version.api_id"))
    api_version = db.Column(db.String, db.ForeignKey("api_version.version"))
    key = db.Column(db.String(255), nullable=False)
    value = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime(), server_default=db.func.now(), server_onupdate=db.func.now()
    )

    def __repr__(self):
        return "<ApiHeader '{}'>".format(self.name)

    def __str__(self):
        return self.name
