from .models import User


def login(data, session):
    user = session.query(User).filter_by(login=data["login"]).one_or_none()
    return user.password == data["password"]


def check_user_exists(user_login, session):
    user = session.query(User).filter_by(login=user_login).one_or_none()
    return user is not None
