from fastapi import FastAPI, status

from db import crud, schemas
from db.database import Base, engine, get_session

Base.metadata.create_all(engine)

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.post("/paper", status_code=status.HTTP_201_CREATED)
def create_paper(paper: schemas.Paper):
    with get_session() as session:
        crud.create_paper(paper, session)
        return f"created paper with id: {paper.id}"


@app.get("/paper/{paper_id}")
def read_paper(paper_id):
    with get_session() as session:
        return crud.read_by_id(paper_id, "paper", session)


@app.put("/paper/{paper_id}")
def update_paper(paper_id, new_values: dict):
    with get_session() as session:
        crud.update_by_id(paper_id, new_values, "paper", session)
        return f"updated paper with id: {paper_id}"


@app.delete("/paper/{paper_id}")
def delete_paper(paper_id):
    with get_session() as session:
        crud.delete_by_id(paper_id, "paper", session)
        return f"deleted paper with id: {paper_id}"
