from app.main import db


class ApiVersionEndpoint(db.Model):  # type: ignore

    __tablename__ = "api_version_endpoint"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    api_id = db.Column(db.Integer, db.ForeignKey("api_version.api_id"))
    version = db.Column(db.String, db.ForeignKey("api_version.version"))
    endpoint = db.Column(db.String, nullable=False)
    method = db.Column(db.String, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    request_body = db.Column(db.String(2048), nullable=False)
    response_body = db.Column(db.String(2048), nullable=False)

    def __repr__(self):
        return "<ApiVersionEndpoint '{}'>".format(self.endpoint)

    def __str__(self):
        return self.endpoint
