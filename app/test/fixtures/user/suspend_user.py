from app.main.model.user_model import User


def suspend_user(db, user_id):
    user = User.query.filter_by(id=user_id).first()
    user.status = "suspended"
    db.session.commit()
    return user
