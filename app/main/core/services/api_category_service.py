from typing import Dict

# , List
from app.main.model.api_category_model import ApiCategory
from app.main.model.user_model import User
from app.main import db
from app.main.utils.exceptions import NotFoundError
from app.main.core.lib.media_manager import MediaManager


class ApiCategoryService:
    def __init__(self, media_manager: MediaManager):
        self.media_manager = media_manager

    def create_category(self, data: Dict, user_id: str) -> ApiCategory:
        new_category = ApiCategory(
            name=data["name"],
            description=data["description"],
            created_by=user_id,
        )
        db.session.add(new_category)
        db.session.commit()
        return new_category

    def get_all_categories(self):
        categories = ApiCategory.query.all()
        result = []
        for category in categories:
            category_dict = {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "created_by": category.created_by,
                "created_at": category.created_at.isoformat(),
                "updated_at": category.updated_at.isoformat(),
                "image": self.media_manager.get_media_url_by_id(category.id),
            }
            result.append(category_dict)
        return result

    def get_category_by_id(self, category_id):
        query = db.session.query(ApiCategory, User).join(
            User, ApiCategory.created_by == User.id
        )

        category = query.filter(ApiCategory.id == category_id).first()

        if category is None:
            raise NotFoundError("No category found with id: {}".format(category_id))

        category, user = category

        category_dict = {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "created_by_id": category.created_by,
            "created_by": {
                "id": user.id,
                "firstname": user.firstname,
                "lastname": user.lastname,
            },
            "created_at": category.created_at.isoformat(),
            "updated_at": category.updated_at.isoformat(),
            "image": self.media_manager.get_media_url_by_id(category.id),
        }

        return category_dict

    def update_category(self, data: Dict, category_id):

        category = ApiCategory.query.filter_by(id=category_id).first()

        if category is None:
            raise NotFoundError("No category found with id: {}".format(category_id))

        if data.get("name", None) is not None:
            category.name = data.get("name", None)

        if data.get("description", None) is not None:
            category.description = data.get("description", None)

        db.session.commit()
