from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Paper, Author, Venue, Lang, Keyword


def create_paper(data: dict, session):
    id = data.get("id", None)
    if id is None:
        return

    paper = session.query(Paper).filter_by(id=id).one_or_none()
    if paper:
        return

    paper = Paper(id=id,
                  title=data.get('title', ''),
                  year=data.get('year', None),
                  n_citations=data.get('n_citations', 0),
                  abstract=data.get('abstract', ''),
                  url=data.get('url', ''),
                  )

    if 'authors' in data:
        author_entries = []
        for author_data in data['authors']:
            author_id = author_data['id']
            author_entry = session.query(Author).filter_by(id=author_id).one_or_none()
            if not author_entry:
                author_entry = Author(id=author_id, name=author_data['name'])

            author_entries.append(author_entry)

        paper.authors = author_entries

    if 'venue' in data:
        venue_id = data['venue']['id']
        venue = session.query(Venue).filter_by(id=venue_id).one_or_none()
        if not venue:
            venue = Venue(id=venue_id, name=data['venue']['name'])

        paper.venue = venue

    if 'lang' in data:
        lang_name = data['lang']
        lang = session.query(Lang).filter_by(name=lang_name).one_or_none()
        if not lang:
            lang = Lang(name=lang_name)

        paper.lang = lang

    if 'keywords' in data:
        keywords = []
        for keyword in data['keywords']:
            keyword_entry = session.query(Keyword).filter_by(name=keyword).one_or_none()
            if not keyword_entry:
                keyword_entry = Keyword(name=keyword)
            keywords.append(keyword_entry)

        paper.keywords = keywords

    session.add(paper)

    session.commit()


def read_paper(id, session):
    paper = session.query(Paper).filter_by(id=id).one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail=f"paper with id {id} not found")

    return paper


def update_paper(id, update_data: dict, session):
    paper = session.query(Paper).filter_by(id=id).one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail=f"paper with id {id} not found")

    for key, value in update_data.items():
        if hasattr(paper, key):
            # to do: add proper updaters (those that create Lang, Keyword, ... entries)
            # currently updating paper.lang throws an error
            setattr(paper, key, value)

    session.commit()


def delete_paper(id, session):
    paper = session.query(Paper).filter_by(id=id).one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail=f"paper with id {id} not found")

    session.delete(paper)

    session.commit()
