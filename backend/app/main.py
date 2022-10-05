import os
from fastapi import FastAPI
from schemas import Paper
from db.db_utils import add_paper, delete_paper, update_paper, read_paper_db
#from db.create_tables import engine

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/paper")
def create_paper(paper: Paper):
    return "create paper"

@app.get("/paper/{id}")
def read_paper(id: str):
    paper = read_paper_db(id)
    return paper

@app.put("/paper/{id}")
def update_todo(id: int):
    return "update paper with id {id}"

@app.delete("/paper/{id}")
def delete_paper(id: int):
    return "delete paper with id {id}"
