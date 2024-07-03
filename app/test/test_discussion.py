import pytest
from app.main.core import ServicesInitializer
from app.main.model.discussion_model import Discussion
from app.main.model.discussion_answer_model import DiscussionAnswer
from app.main.utils.exceptions import NotFoundError
from app.main.model.api_model import ApiModel
from .fixtures.discussion.add_discussion import add_discussion
from .fixtures.discussion.add_answer import add_answer

ApiDiscussionService = ServicesInitializer.a_discussion_service()


@pytest.fixture(scope="module")
def test_api(test_db):
    api = ApiModel(
        name="Test API",
        description="Test API Description",
        category_id=1,
        supplier_id=1,
    )
    test_db.session.add(api)
    test_db.session.commit()
    yield api
    test_db.session.delete(api)
    test_db.session.commit()


def test_get_all_by_api_id(test_db, test_api):
    api_id = test_api.id
    add_discussion(
        db=test_db, api_id=api_id, title="Test Discussion", question="Test Question"
    )
    discussions = ApiDiscussionService.get_all_by_api_id(api_id)
    assert len(discussions) == 1
    assert discussions[0].api_id == api_id


def test_get_by_id_not_found():
    with pytest.raises(NotFoundError):
        ApiDiscussionService.get_by_id(999)


def test_get_by_id(test_db, test_api):
    discussion = add_discussion(
        test_db, api_id=test_api.id, title="Test Discussion", question="Test Question"
    )
    fetched_discussion = ApiDiscussionService.get_by_id(discussion.id)
    assert fetched_discussion.id == discussion.id


def test_create_new_discussion(test_db, test_api):
    api_id = test_api.id
    data = {"title": "New Discussion", "question": "New Question"}
    new_discussion = ApiDiscussionService.create_new_discussion(api_id, data, 1)
    assert new_discussion.title == data["title"]
    assert new_discussion.question == data["question"]
    discussion = Discussion.query.get(new_discussion.id)
    assert discussion is not None


def test_create_new_discussion_with_api_not_found():
    api_id = 999
    data = {"title": "New Discussion", "question": "New Question"}
    with pytest.raises(NotFoundError):
        ApiDiscussionService.create_new_discussion(api_id, data, 1)


def test_delete_discussion(test_db):
    discussion = add_discussion(
        test_db, api_id=1, title="Test Discussion", question="Test Question"
    )
    deleted_discussion = ApiDiscussionService.delete_discussion(discussion.id)
    assert deleted_discussion.id == discussion.id
    assert Discussion.query.get(deleted_discussion.id) is None


def test_create_new_answer(test_db):
    discussion = add_discussion(
        test_db, api_id=1, title="Test Discussion", question="Test Question"
    )
    data = {"answer": "Test Answer"}
    new_answer = ApiDiscussionService.create_new_answer(discussion.id, data, 1)
    assert new_answer.answer == data["answer"]
    assert new_answer.discussion_id == discussion.id
    assert DiscussionAnswer.query.get(new_answer.id) is not None


def test_get_answer_by_id(test_db):
    discussion = add_discussion(
        test_db, api_id=1, title="Test Discussion", question="Test Question"
    )
    answer = add_answer(test_db, discussion_id=discussion.id, answer="Test Answer")
    fetched_answer = ApiDiscussionService.get_answer_by_id(answer.id)
    assert fetched_answer.id == answer.id


def test_delete_answer(test_db):
    discussion = add_discussion(
        test_db, api_id=1, title="Test Discussion", question="Test Question"
    )
    answer = add_answer(test_db, discussion_id=discussion.id, answer="Test Answer")
    deleted_answer = ApiDiscussionService.delete_answer(answer.id)
    assert deleted_answer.id == answer.id
    assert DiscussionAnswer.query.get(deleted_answer.id) is None
