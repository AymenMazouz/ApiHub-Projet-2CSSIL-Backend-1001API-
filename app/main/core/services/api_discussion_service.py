from typing import Dict, List
from app.main.model.discussion_model import Discussion
from app.main.model.discussion_answer_model import DiscussionAnswer
from app.main import db
from app.main.utils.exceptions import NotFoundError
from app.main.model.api_model import ApiModel
from app.main.model.answer_vote_model import AnswerVote


class ApiDiscussionService:
    def get_all_by_api_id(self, api_id: int) -> List[Discussion]:
        if ApiModel.query.filter_by(id=api_id).first() is None:
            raise NotFoundError("No API found with id: {}".format(api_id))

        discussions = Discussion.query.filter_by(api_id=api_id).all()
        return discussions

    def get_by_id(self, discussion_id: int):
        discussion = Discussion.query.filter_by(id=discussion_id).first()
        if not discussion:
            raise NotFoundError("No discussion found with id: {}".format(discussion_id))
        return discussion

    def create_new_discussion(
        self, api_id: int, data: dict, user_id: int
    ) -> Discussion:
        if ApiModel.query.filter_by(id=api_id).first() is None:
            raise NotFoundError("No API found with id: {}".format(api_id))

        new_discussion = Discussion(
            title=data["title"],
            question=data["question"],
            user_id=user_id,
            api_id=api_id,
        )
        db.session.add(new_discussion)
        db.session.commit()
        return new_discussion

    def delete_discussion(self, discussion_id: int):
        if Discussion.query.filter_by(id=discussion_id).first() is None:
            raise NotFoundError("No discussion found with id: {}".format(discussion_id))

        discussion = Discussion.query.filter_by(id=discussion_id).first()
        db.session.delete(discussion)
        db.session.commit()
        return discussion

    def create_new_answer(self, discussion_id, data: Dict, user_id: int):
        if Discussion.query.filter_by(id=discussion_id).first() is None:
            raise NotFoundError("No discussion found with id: {}".format(discussion_id))

        new_answer = DiscussionAnswer(
            discussion_id=discussion_id,
            user_id=user_id,
            answer=data["answer"],
        )
        db.session.add(new_answer)
        db.session.commit()
        return new_answer

    def get_answer_by_id(self, answer_id: int) -> DiscussionAnswer:
        answer = DiscussionAnswer.query.filter_by(id=answer_id).first()
        if not answer:
            raise NotFoundError("No answer found with id: {}".format(answer_id))

        return answer

    def delete_answer(self, answer_id: int) -> DiscussionAnswer:
        answer = DiscussionAnswer.query.filter_by(id=answer_id).first()
        if not answer:
            raise NotFoundError("No answer found with id: {}".format(answer_id))
        db.session.delete(answer)
        db.session.commit()
        return answer

    def vote_on_answer(self, answer_id: int, user_id: int, vote: str) -> None:

        if DiscussionAnswer.query.filter_by(id=answer_id).first() is None:
            raise NotFoundError("No answer found with id: {}".format(answer_id))

        existing_vote: AnswerVote = AnswerVote.query.filter_by(
            answer_id=answer_id, user_id=user_id
        ).first()

        if existing_vote:
            existing_vote.vote = vote
            db.session.commit()
            return

        vote = AnswerVote(answer_id=answer_id, user_id=user_id, vote=vote)
        db.session.add(vote)
        db.session.commit()
        return

    def remove_vote(self, answer_id: int, user_id: int) -> None:
        if DiscussionAnswer.query.filter_by(id=answer_id).first() is None:
            raise NotFoundError("No answer found with id: {}".format(answer_id))

        vote = AnswerVote.query.filter_by(answer_id=answer_id, user_id=user_id).first()
        if not vote:
            raise NotFoundError(
                "No vote found for user: {} and answer: {}".format(user_id, answer_id)
            )
        db.session.delete(vote)
        db.session.commit()
        return

    def get_user_vote(self, answer_id: int, user_id: int) -> AnswerVote:
        if DiscussionAnswer.query.filter_by(id=answer_id).first() is None:
            raise NotFoundError("No answer found with id: {}".format(answer_id))

        vote = AnswerVote.query.filter_by(answer_id=answer_id, user_id=user_id).first()
        if not vote:
            raise NotFoundError(
                "No vote found for user_id: {} and answer_id: {}".format(
                    user_id, answer_id
                )
            )
        return vote
