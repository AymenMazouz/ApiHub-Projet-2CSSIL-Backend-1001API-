from app.main.model.api_category_model import ApiCategory


def add_category(db, name, description, user_id):
    new_category = ApiCategory(name=name, description=description, created_by=user_id)
    db.session.add(new_category)
    db.session.commit()
    return new_category
