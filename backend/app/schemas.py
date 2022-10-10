from pydantic import BaseModel


class Author(BaseModel):
    id: str
    name: str


class Venue(BaseModel):
    id: str
    name: str


class Lang(BaseModel):
    name: str


class Keyword(BaseModel):
    name: str


class Paper(BaseModel):
    id: str
    title: str
    year: int
    authors: list[Author]
    venue: Venue
    n_citations: int
    keywords: list[str]
    abstract: str
    url: str
    lang: str
