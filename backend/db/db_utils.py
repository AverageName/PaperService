from models import User


def login(data, session):
    user = session.query(User).filter_by(login=data['login']).one_or_none()
        
    if user.password != data['password']:
        return False
    
    return True


def check_user_exists(login, session):
    user = session.query(User).filter_by(login=login).one_or_none()
    
    if user is None:
        return False
    
    return True
