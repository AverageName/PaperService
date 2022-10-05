from pydantic import BaseModel
from typing import List


class Paper(BaseModel):
    id: str
    title: str
    year: int
    authors: List[dict]
    venue: dict
    n_citations: int
    keywords: List[str]
    abstract: str
    url: str
    lang: str
