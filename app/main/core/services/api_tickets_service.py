from app.main.model.api_ticket_model import ApiTicket
from app.main.model.api_model import ApiModel
from app.main.model.user_model import User
from app.main.utils.exceptions import NotFoundError, BadRequestError
from datetime import datetime
from app.main import db


class ApiTicketsService:

    def create_ticket(self, api_id: str, ticket: dict, user_id: str):
        if ApiModel.query.filter_by(id=api_id).first() is None:
            raise NotFoundError("API not found")

        if (
            ticket.get("subject") is None
            or ticket.get("description") is None
            or ticket.get("type") is None
        ):
            raise BadRequestError("Subject and description are required")

        new_ticket = ApiTicket(
            api_id=api_id,
            user_id=user_id,
            subject=ticket.get("subject"),
            description=ticket.get("description"),
            ticket_type=ticket.get("type"),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        db.session.add(new_ticket)
        db.session.commit()

        return new_ticket

    def get_tickets(self, api_id: str):
        tickets = (
            db.session.query(ApiTicket, User)
            .join(User, ApiTicket.user_id == User.id)
            .filter(ApiTicket.api_id == api_id)
            .all()
        )
        return [
            {
                "id": ticket.id,
                "subject": ticket.subject,
                "description": ticket.description,
                "response": ticket.response,
                "created_at": ticket.created_at.isoformat(),
                "updated_at": ticket.updated_at.isoformat(),
                "type": ticket.ticket_type,
                "status": "closed" if ticket.response else "open",
                "api_id": ticket.api_id,
                "user": {
                    "id": user.id,
                    "firstname": user.firstname,
                    "lastname": user.lastname,
                },
            }
            for ticket, user in tickets
        ]

    def respond_to_ticket(
        self, supplier_id: str, api_id: str, ticket_id: str, response: dict
    ):
        # verify that the api_id belongs to the supplier
        api = ApiModel.query.filter_by(id=api_id).first()
        if api is None or api.supplier_id != supplier_id:
            raise NotFoundError("API not found")

        ticket = ApiTicket.query.filter_by(id=ticket_id, api_id=api_id).first()

        if ticket is None:
            raise NotFoundError("Ticket not found")

        if ticket.response:
            raise BadRequestError("Ticket already closed")

        if response.get("response") is None:
            raise BadRequestError("Response is required")

        ticket.response = response.get("response")

        db.session.commit()
