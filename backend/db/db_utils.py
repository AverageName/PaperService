from sqlalchemy import insert, select
from create_tables import *
from sqlalchemy.orm import Session, sessionmaker


def create_session(): 
    engine = create_engine(f"postgresql+psycopg2://postgres:{os.environ['POSTGRES_PASSWORD']}@postgres/papers")
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def add_paper(data):
    session = create_session()

    id = data.get("id", None)
    if id is None:
        return
    papers = session.query(Paper).filter(Paper.id == id).all()
    if len(papers) > 0:
        return

    paper = Paper(id=id,
                  title=data.get('title', ''),
                  year=data.get('year', None),
                  n_citations=data.get('n_citations', 0),
                  abstract=data.get('abstract', ''),
                  url=data.get('url', ''),
                  )
    session.add(paper)
    session.commit()
    
    if 'authors' in data:
        author_ids = [author['_id'] for author in data['authors']]
        authors = []
        for idx, author_id in enumerate(author_ids):
            authors = session.query(Author).filter(Author.id == author_id).all()
            if len(authors) > 0:
                authors.append(authors[0])
            else:
                author = Author(id=data['authors'][idx]['_id'], name=data['authors'][idx]['name'])
                session.add(author)
                authors.append(author)
        paper.authors = authors
        
    if 'venue' in data:
        venue_id = data['venue']['_id']
        venues = session.query(Venue).filter(Venue.id == venue_id).all()    
        if len(venues) > 0:
            paper.venue = venues[0]
        else:
            venue = Venue(id=venue_id, name=data['venue']['name'])
            paper.venue = venue
            session.add(venue)

    if 'lang' in data:
        lang_name = data['lang']
        langs = session.query(Lang).filter(Lang.name == lang_name).all()
        if len(langs) > 0:
            paper.lang = langs[0]
        else:
            lang = Lang(name=lang_name)
            paper.lang = lang
            session.add(lang)

    session.commit()
    session.close()
    
    return


def read_paper(id):
    session = create_session()
    papers = session.query(Paper).filter(Paper.id == id).all()
    session.close()
    if len(papers) > 0:
        return papers[0]
    else:
        return []
    
def update_paper(id, data):
    session = create_session()
    papers = session.query(Paper).filter(Paper.id == id).all()
    if len(papers) > 0:
        pydantic_dict = data.dict()
        for key in pydantic_dict.keys():
            update_dict = {key: pydantic_dict[key]}
            paper.update(update_dict)
    else:
        session.close()
        return


def delete_paper(id):
    session = create_session()
    papers = session.query(Paper).filter(Paper.id == id).all()
    if len(papers) > 0:
        session.delete(papers[0])
        session.commit()
    session.close()

    return

if __name__ == "__main__":
    
    r = add_paper({ 
        "id" : "53e99784b7602d9701f3e3f5", 
        "title" : "3GIO.", 
        "venue" : {
            "_id" : "sdksd",
            "name" : "CVPR"
        }, 
        "year" : 2011, 
        "keywords" : ["Cars"], 
        "n_citation" : 0, 
        "lang" : "e"
    })

    print(read_paper("53e99784b7602d9701f3e3f5"))

    session = create_session()
    papers = session.query(Paper).all()
    print(papers)
