import crud
from database import Base, SessionLocal, engine
from fastapi import Depends, FastAPI, status
from sqlalchemy.orm import Session

import schemas

Base.metadata.create_all(engine)

app = FastAPI()


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.post("/paper", status_code=status.HTTP_201_CREATED)
def create_paper(paper: schemas.Paper, session: Session = Depends(get_session)):
    crud.create_paper(paper, session)
    return f"created paper with id: {paper.id}"


@app.get("/paper/{paper_id}")
def read_paper(paper_id, session: Session = Depends(get_session)):
    return crud.read_by_id(paper_id, "paper", session)


@app.put("/paper/{paper_id}")
def update_paper(paper_id, new_values: dict, session: Session = Depends(get_session)):
    crud.update_by_id(paper_id, new_values, "paper", session)
    return f"updated paper with id: {paper_id}"


@app.delete("/paper/{paper_id}")
def delete_paper(paper_id, session: Session = Depends(get_session)):
    crud.delete_by_id(paper_id, "paper", session)
    return f"deleted paper with id: {paper_id}"
