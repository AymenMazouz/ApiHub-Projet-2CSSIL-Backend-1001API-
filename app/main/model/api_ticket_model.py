from app.main import db


class ApiTicket(db.Model):  # type: ignore
    __tablename__ = "api_ticket"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    api_id = db.Column(db.Integer, db.ForeignKey("api.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    subject = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    ticket_type = db.Column(db.String, nullable=True)
    response = db.Column(db.String, nullable=True)
