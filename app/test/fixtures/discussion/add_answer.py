from app.main.model.discussion_answer_model import DiscussionAnswer


def add_answer(db, discussion_id, answer, user_id=2):
    answer = DiscussionAnswer(
        discussion_id=discussion_id, answer=answer, user_id=user_id
    )
    db.session.add(answer)
    db.session.commit()
    return answer
