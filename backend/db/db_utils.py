from .models import User, Paper, Author


def check_user_exists(user_login, session):
    user = session.query(User).filter_by(tg_id=user_login).one_or_none()
    return user is not None


def find_by_year(year, session):
    papers = session.query(Paper).filter_by(year=year).limit(20).all()
    res = []
    if papers is not None:
        res = [paper.as_dict() for paper in papers]
    return res


def find_by_author(author, session):
    author = session.query(Author).filter_by(name=author).one_or_none()
    res = []
    if author is not None:
        papers = author.papers
        res = [paper.as_dict() for paper in papers[:20]]
    return res


def find_by_topic(topic, session):
    papers = session.query(Paper).filter_by(topic=topic).limit(20).all()
    res = []
    if papers is not None:
        res = [paper.as_dict() for paper in papers]
    return res


def top_10_authors(topic, session):
    authors = session.query(Author).join(Author.papers).filter_by(topic=topic).group_by(Author.id).limit(10).all()
    res = []
    if authors is not None:
        res = [author.as_dict() for author in authors]
    return res
