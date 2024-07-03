import pytest
from flask import g
from http import HTTPStatus
from app.main.utils.roles import Role
from app.main.utils.decorators.discussion import check_delete_discussion_permission
from .fixtures.discussion.add_discussion import add_discussion


# Fixture to set up a discussion and a user
@pytest.fixture
def setup_discussion_user(test_db):

    user_id = 1
    discussion = add_discussion(
        test_db,
        api_id=1,
        title="Test Discussion",
        question="Test Question",
        user_id=user_id,
    )

    return user_id, discussion


# Test the decorator with an unauthorized user
def test_check_delete_discussion_permission_unauthorized(
    test_db, setup_discussion_user, app
):
    user_id, discussion = setup_discussion_user

    with app.test_request_context():
        g.user = {"id": user_id + 1, "role": Role.USER}
        response, status_code = check_delete_discussion_permission(
            lambda *args, **kwargs: ("OK", HTTPStatus.OK)
        )(discussion_id=discussion.id)
        assert status_code == HTTPStatus.UNAUTHORIZED


# Test the decorator with an authorized user
def test_check_delete_discussion_permission_admin_authorized(
    test_db, setup_discussion_user, app
):
    user_id, discussion = setup_discussion_user

    with app.test_request_context():
        g.user = {"id": user_id + 1, "role": Role.ADMIN}
        response, status_code = check_delete_discussion_permission(
            lambda *args, **kwargs: ("OK", HTTPStatus.OK)
        )(discussion_id=discussion.id)
        assert status_code == HTTPStatus.OK
        assert response == "OK"


def test_check_delete_discussion_permission_user_authorized(
    test_db, setup_discussion_user, app
):
    user_id, discussion = setup_discussion_user

    with app.test_request_context():
        g.user = {"id": user_id, "role": Role.USER}
        response, status_code = check_delete_discussion_permission(
            lambda *args, **kwargs: ("OK", HTTPStatus.OK)
        )(discussion_id=discussion.id)
        assert status_code == HTTPStatus.OK
        assert response == "OK"
