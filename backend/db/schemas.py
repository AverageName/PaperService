from typing import Optional

from pydantic import BaseModel


class Author(BaseModel):
    id: str
    name: Optional[str]


class Venue(BaseModel):
    id: str
    name: Optional[str]


class Paper(BaseModel):
    id: str
    title: Optional[str]
    year: Optional[int]
    authors: Optional[list[Author]]
    venue: Optional[Venue]
    n_citations: Optional[int]
    keywords: Optional[list[str]]
    abstract: Optional[str]
    # to do: think about storing a list in the model in a better way
    url: Optional[list[str]]
    lang: Optional[str]
