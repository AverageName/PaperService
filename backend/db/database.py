import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE_URL = (
    f"postgresql+psycopg2://postgres:{os.environ['POSTGRES_PASSWORD']}@postgres/papers"
)

engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
