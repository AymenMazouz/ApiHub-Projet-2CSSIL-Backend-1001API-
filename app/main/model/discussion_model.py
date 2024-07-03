from app.main import db


class Discussion(db.Model):  # type: ignore
    __tablename__ = "discussion"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    question = db.Column(db.String, nullable=False)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE", name="fk_discussion_user_id"),
        nullable=False,
    )
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    api_id = db.Column(
        db.Integer,
        db.ForeignKey("api.id", ondelete="CASCADE", name="fk_discussion_api_id"),
        nullable=False,
    )
    answers = db.relationship("DiscussionAnswer", passive_deletes=True)
    user = db.relationship("User", backref="discussions", passive_deletes=True)

    def __repr__(self):
        return "<Discussion '{}'>".format(self.id)

    def __str__(self):
        return self.id
