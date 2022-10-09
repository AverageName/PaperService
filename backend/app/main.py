from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy.orm import Session
import schemas
from database import Base, engine, SessionLocal
import crud

Base.metadata.create_all(engine)

app = FastAPI()

# Helper function to get database session


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
    crud.create_paper(paper.dict(), session)
    return f"created paper with id: {paper.id}"


@app.get("/paper/{id}")
def read_paper(id: str, session: Session = Depends(get_session)):
    return crud.read_paper(id, session)


@app.put("/paper/{id}")
def update_paper(id: str, update_data: dict, session: Session = Depends(get_session)):
    crud.update_paper(id, update_data, session)
    return f"updated paper with id: {id}"


@app.delete("/paper/{id}")
def delete_paper(id: str, session: Session = Depends(get_session)):
    crud.delete_paper(id, session)
    return "deleted paper with id: {id}"
