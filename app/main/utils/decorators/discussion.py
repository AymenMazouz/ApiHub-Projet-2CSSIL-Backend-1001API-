from typing import Callable
from functools import wraps
from flask import g
from http import HTTPStatus
from app.main.utils.roles import Role
from app.main.core import ServicesInitializer

ApiDiscussionService = ServicesInitializer.a_discussion_service()


def check_delete_discussion_permission(f: Callable) -> Callable:
    """
    Check if the user has permission to delete a discussion.
    must be used after `require_authentication`"""

    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.user:
            raise Exception("User not found in g object")
        discussion_id = kwargs.get("discussion_id")
        discussion = ApiDiscussionService.get_by_id(discussion_id)
        if (g.user.get("role") != Role.ADMIN) and (
            g.user.get("id") != discussion.user_id
        ):
            response = {
                "status": "fail",
                "message": "You do not have permission to delete this discussion",
            }
            return response, HTTPStatus.UNAUTHORIZED
        return f(*args, **kwargs)

    return decorated


def check_delete_answer_permission(f: Callable) -> Callable:
    """
    Check if the user has permission to delete an answer.
    must be used after `require_authentication`"""

    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.user:
            raise Exception("User not found in g object")
        answer_id = kwargs.get("answer_id")
        answer = ApiDiscussionService.get_answer_by_id(answer_id)
        if (g.user.get("role") != Role.ADMIN) and (g.user.get("id") != answer.user_id):
            response = {
                "status": "fail",
                "message": "You do not have permission to delete this answer",
            }
            return response, HTTPStatus.UNAUTHORIZED
        return f(*args, **kwargs)

    return decorated
