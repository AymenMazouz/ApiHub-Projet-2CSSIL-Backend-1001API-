from unittest.mock import Mock
import pytest
from app.main.model.api_category_model import ApiCategory
from app.main.model.user_model import User
from .fixtures.category.add_category import add_category
from app.main.core.services.api_category_service import ApiCategoryService
from app.main.core.lib.impl.media_manager_impl import MediaManagerImpl
from app.main.utils.exceptions import NotFoundError


@pytest.fixture(scope="module")
def api_category_service(test_db):

    mock_media_manager = Mock(spec=MediaManagerImpl)
    mock_media_manager.get_media_url_by_id.side_effect = (
        lambda media_id: f"https://example.com/media_{media_id}.jpg"
    )

    return ApiCategoryService(media_manager=mock_media_manager)


def test_get_all_categories(test_db, api_category_service):
    new_category = add_category(
        db=test_db,
        name="New Category",
        description="New Category description",
        user_id=1,
    )
    categories = api_category_service.get_all_categories()
    assert len(categories) == 1
    assert categories[0]["id"] == new_category.id


def test_get_categorie_by_id(test_db, api_category_service):
    new_category = add_category(
        db=test_db,
        name="New Category",
        description="New Category description",
        user_id=1,
    )
    user = User.query.get(1)
    expected_result = {
        "id": new_category.id,
        "name": new_category.name,
        "description": new_category.description,
        "created_by_id": new_category.created_by,
        "created_by": {
            "id": user.id,
            "firstname": user.firstname,
            "lastname": user.lastname,
        },
        "created_at": new_category.created_at.isoformat(),
        "updated_at": new_category.updated_at.isoformat(),
        "image": f"https://example.com/media_{new_category.id}.jpg",
    }
    result = api_category_service.get_category_by_id(new_category.id)
    assert result == expected_result


def test_get_category_by_id_not_found(api_category_service):
    with pytest.raises(NotFoundError, match=r"No category found with id: \d+"):
        api_category_service.get_category_by_id(999)


def test_create_new_category(test_db, api_category_service):
    data = {"name": "New Category", "description": "New description"}
    new_category = api_category_service.create_category(data, 1)
    assert new_category.name == data["name"]
    assert new_category.description == data["description"]
    category = ApiCategory.query.get(new_category.id)
    assert category is not None
