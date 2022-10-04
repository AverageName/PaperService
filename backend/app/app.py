from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/paper"):
def create_paper():
    return "create paper"

@app.get("/paper/{id}):
def read_paper(id: int):
    return "read paper with id {id}"

@app.put("/paper/{id}")
def update_todo(id: int):
    return "update paper with id {id}"

@app.delete("/paper/{id}")
def delete_paper(id: int):
    return "delete paper with id {id}"
