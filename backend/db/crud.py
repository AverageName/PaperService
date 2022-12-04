import sys
from fastapi import HTTPException
from sqlalchemy.orm import Session
from topic_modeling.predict import predict_topic
from . import models, schemas


def create_by_str(datum: str, model, session: Session):
    entry = session.query(model).filter_by(id=datum).one_or_none()
    if not entry:
        # str models store their value as .id
        entry = model(id=datum)
        session.add(entry)
        session.commit()

    return entry


def create_by_id(datum, model, session: Session):
    entry = session.query(model).filter_by(id=datum.id).one_or_none()
    if not entry:
        entry = model(**datum.dict())
        session.add(entry)
        session.commit()

    return entry


def create_many_by_str(data: set[str], model, session: Session):
    return [create_by_str(datum, model, session) for datum in data]


def create_many_by_id(data: list, model, session: Session):
    ids_left_to_create = {datum.id for datum in data}
    created_entries = []
    for datum in data:
        if datum.id in ids_left_to_create:
            created_entries.append(create_by_id(datum, model, session))
            ids_left_to_create.remove(datum.id)

    return created_entries


def create_paper(paper: schemas.Paper, session) -> models.Paper:
    entry = session.query(models.Paper).filter_by(id=paper.id).one_or_none()
    if not entry:
        topics = predict_topic(paper.title)
        print(topics, file=sys.stderr)
        entry = models.Paper(
            id=paper.id,
            title=paper.title,
            year=paper.year,
            n_citations=paper.n_citations,
            abstract=paper.abstract,
            url=paper.url,
            topic=topics[1]
        )

        if paper.authors:
            entry.authors = create_many_by_id(paper.authors, models.Author, session)
        if paper.venue:
            entry.venue = create_by_id(paper.venue, models.Venue, session)
        if paper.keywords:
            entry.keywords = create_many_by_str(set(paper.keywords), models.Keyword, session)
        if paper.lang:
            entry.lang = create_by_str(paper.lang, models.Lang, session)

        session.add(entry)
        session.commit()

    return entry


def throw_not_found(entry_id):
    raise HTTPException(status_code=404, detail=f"entry with id: {entry_id} is not found")


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
        return create_many_by_str(value, models.Keyword, session)
    if attribute == "lang":
        return create_by_str(value, models.Lang, session)

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
            setattr(entry, attribute, create_attribute_value(attribute, new_value, session))
        else:
            setattr(entry, attribute, new_value)

    session.commit()


def delete_by_id(entry_id, table_name: str, session: Session):
    entry = session.query(get_table(table_name)).filter_by(id=entry_id).one_or_none()
    if not entry:
        throw_not_found(entry_id)

    session.delete(entry)
    session.commit()


def create_user(tg_id, session):
    user = session.query(models.User).filter_by(tg_id=tg_id).one_or_none()
    if user is not None:
        raise HTTPException(status_code=404, detail="User with this login already exists")

    user = models.User(tg_id=tg_id)

    session.add(user)
    print("User has been created", file=sys.stderr)
    session.commit()
