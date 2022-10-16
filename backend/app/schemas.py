from pydantic import BaseModel


class Author(BaseModel):
    id: str
    name: str


class Venue(BaseModel):
    id: str
    name: str


class Keyword(BaseModel):
    id: str


class Lang(BaseModel):
    id: str


# to do: define typing.Optional values
class Paper(BaseModel):
    id: str
    title: str
    year: int
    authors: list[Author]
    venue: Venue
    n_citations: int
    keywords: list[Keyword]
    abstract: str
    url: str
    lang: Lang
