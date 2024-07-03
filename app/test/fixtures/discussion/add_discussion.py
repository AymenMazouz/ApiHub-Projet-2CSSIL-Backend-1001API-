from app.main.model.discussion_model import Discussion


def add_discussion(db, api_id, title, question, user_id=1):
    discussion = Discussion(
        api_id=api_id, title=title, question=question, user_id=user_id
    )
    db.session.add(discussion)
    db.session.commit()
    return discussion
