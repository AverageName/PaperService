import os
import psycopg2
import sys
from sqlalchemy import create_engine, MetaData, Table, String, Integer, Column, ForeignKey
from sqlalchemy_utils import database_exists, create_database


metadata = MetaData()

author = Table('author', metadata,
       Column('id', String(100), primary_key=True),
       Column('name', String(100))
)

venue = Table('venue', metadata,
       Column('id', String(100), primary_key=True),
       Column('name', String(500))
)

lang = Table('lang', metadata,
       Column('id', String(100), primary_key=True),
       Column('name', String(100))
)

keyword = Table('keyword', metadata,
       Column('id', String(100), primary_key=True),
       Column('name', String(200))
)

paper = Table('paper', metadata,
      Column('id', String(100), primary_key=True),
      Column('title', String(500)),
      Column('year', Integer()),
      Column('venue_id', ForeignKey("venue.id")),
      Column('n_citations', Integer(), default=0),
      Column('abstract', String(1000)),
      Column('url', String(500)),
      Column('lang_id', ForeignKey("lang.id"))
)

paper_author = Table('paper_author', metadata,
             Column('paper_id', ForeignKey('paper.id')),
             Column('author_id', ForeignKey('author.id'))
)

paper_keyword = Table('paper_keyword', metadata,
              Column('paper_id', ForeignKey('paper.id')),
              Column('keyword_id', ForeignKey('keyword.id'))
)

paper_paper = Table('paper_paper', metadata,
            Column('paper_id_1', ForeignKey('paper.id')),
            Column('paper_id_2', ForeignKey('paper.id'))
)

engine = create_engine(f"postgresql+psycopg2://postgres:{os.environ['POSTGRES_PASSWORD']}@postgres/papers")
if not database_exists(engine.url):
    create_database(engine.url)
engine.connect()
metadata.create_all(engine)

