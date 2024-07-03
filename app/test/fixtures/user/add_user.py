from app.main.model.user_model import User


def add_user(db, email, firstname, lastname, password):
    new_user = User(
        email=email, password=password, firstname=firstname, lastname=lastname
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user
