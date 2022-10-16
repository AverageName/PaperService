import sys
from fastapi import HTTPException
from sqlalchemy.orm import Session
import models
import schemas


def create_by_id(schema, model, session: Session):
    entry = session.query(model).filter_by(id=schema.id).one_or_none()
    if not entry:
        entry = model(**schema.dict())
        session.add(entry)
        session.commit()

    return entry


def create_many_by_id(schemas: list, model, session: Session):
    return [create_by_id(schema, model, session) for schema in schemas]


def create_paper(paper: schemas.Paper, session) -> models.Paper:
    entry = session.query(models.Paper).filter_by(id=paper.id).one_or_none()
    if not entry:
        entry = models.Paper(
            id=paper.id,
            title=paper.title,
            year=paper.year,
            authors=create_many_by_id(paper.authors, models.Author, session),
            venue=create_by_id(paper.venue, models.Venue, session),
            n_citations=paper.n_citations,
            keywords=create_many_by_id(paper.keywords, models.Keyword, session),
            abstract=paper.abstract,
            url=paper.url,
            lang=create_by_id(paper.lang, models.Lang, session),
        )
        session.add(entry)
        session.commit()

    return entry


def throw_not_found(entry_id):
    raise HTTPException(
        status_code=404, detail=f"entry with id: {entry_id} is not found"
    )


def get_table(table_name: str):
    if table_name == "paper":
        return models.Paper
    if table_name == "author":
        return models.Author
    if table_name == "venue":
        return models.Venue
    if table_name == "keyword":
        return models.Keyword
    if table_name == "lang":
        return models.Lang

    raise HTTPException(status_code=404, detail=f"table: {table_name} not found")


def read_by_id(entry_id, table_name: str, session: Session):
    entry = session.query(get_table(table_name)).filter_by(id=entry_id).one_or_none()
    if not entry:
        throw_not_found(entry_id)

    return entry


def create_attribute_value(attribute, value, session):
    if attribute == "authors":
        return create_many_by_id(
            [schemas.Author(**author) for author in value], models.Author, session
        )
    if attribute == "venue":
        return create_by_id(schemas.Venue(**value), models.Venue, session)
    if attribute == "keywords":
        return create_many_by_id(
            [schemas.Keyword(**keyword) for keyword in value], models.Keyword, session
        )
    if attribute == "lang":
        return create_by_id(schemas.Lang(**value), models.Lang, session)

    return value


def update_by_id(entry_id, new_values: dict, table_name: str, session: Session):
    entry = session.query(get_table(table_name)).filter_by(id=entry_id).one_or_none()
    if not entry:
        throw_not_found(entry_id)

    for attribute, new_value in new_values.items():
        if not hasattr(entry, attribute):
            raise HTTPException(
                status_code=400, detail=f"entry does not have attribute: {attribute}"
            )

        # this is currently the only table that has attributes that are themselves tables
        if table_name == "paper":
            setattr(
                entry, attribute, create_attribute_value(attribute, new_value, session)
            )
        else:
            setattr(entry, attribute, new_value)

    session.commit()


def delete_by_id(entry_id, table_name: str, session: Session):
    entry = session.query(get_table(table_name)).filter_by(id=entry_id).one_or_none()
    if not entry:
        throw_not_found(entry_id)

    session.delete(entry)
    session.commit()


def create_user(data, session):
    user = session.query(User).filter_by(login=data['login']).one_or_none()
    if user is not None:
        raise HTTPException(status_code=404, detail=f"User with this login already exists")

    user = User(login=data['login'], password=data['password'])
    
    session.add(user)
    print("User has been created", file=sys.stderr)
    session.commit()
