import os
import unittest

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from .. import crud, models, schemas
from ..database import Base, get_session


class TestCrud(unittest.TestCase):
    TEST_DATABASE_URL = (
        f"postgresql+psycopg2://postgres:{os.environ['POSTGRES_PASSWORD']}@postgres/test_db"
    )

    @classmethod
    def setUpClass(cls):
        assert not database_exists(cls.TEST_DATABASE_URL)
        create_database(cls.TEST_DATABASE_URL)

        cls.engine = create_engine(cls.TEST_DATABASE_URL)

        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(bind=cls.engine, expire_on_commit=False)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()
        drop_database(cls.TEST_DATABASE_URL)

    def test_paper_crud(self):
        table_name = models.Paper.__tablename__

        paper_id = "string"
        paper_dict = {
            "id": paper_id,
            "title": "string",
            "year": 0,
            "authors": [{"id": "string", "name": "string"}],
            "venue": {"id": "string", "name": "string"},
            "n_citations": 0,
            "keywords": ["string"],
            "abstract": "string",
            "url": ["string"],
            "lang": "string",
        }

        with get_session(self.SessionLocal) as session:

            created_paper = crud.create_paper(schemas.Paper(**paper_dict), session)
            self.assertEqual(created_paper.id, paper_id)

            read_paper = crud.read_by_id(paper_id, table_name, session)
            self.assertIs(created_paper, read_paper)

            new_title = "Alice"
            crud.update_by_id(
                paper_id,
                {"title": new_title},
                table_name,
                session,
            )
            self.assertEqual(created_paper.title, new_title)

            crud.delete_by_id(paper_id, table_name, session)
            with self.assertRaises(HTTPException):
                crud.read_by_id(paper_id, table_name, session)

            self.assertEqual(session.query(models.Paper).count(), 0)

    def test_empty_paper(self):
        table_name = models.Paper.__tablename__

        paper_id = "string"
        paper_dict = {"id": paper_id}

        with get_session(self.SessionLocal) as session:

            created_paper = crud.create_paper(schemas.Paper(**paper_dict), session)
            self.assertEqual(created_paper.id, paper_id)

            new_title = "Alice"
            crud.update_by_id(
                paper_id,
                {"title": new_title},
                table_name,
                session,
            )

            read_paper = crud.read_by_id(paper_id, table_name, session)
            self.assertEqual(read_paper.title, new_title)

    def test_extra_attributes(self):
        extra_attribute = "doi"
        self.assertFalse(hasattr(models.Paper, extra_attribute))

        paper_dict = {"id": "string", extra_attribute: "string"}

        with get_session(self.SessionLocal) as session:
            crud.create_paper(schemas.Paper(**paper_dict), session)

    def test_venue_no_id(self):
        paper_dict = {"id": "string", "venue": {"raw": "string"}}

        with self.assertRaises(ValidationError):
            schemas.Paper(**paper_dict)
