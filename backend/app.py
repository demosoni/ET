from fastapi import FastAPI
from pydantic import BaseModel
from backend.agents import run_agents

app = FastAPI()

class Query(BaseModel):
    query: str
    location: str = None
    crop: str = None
    soil: str = None

@app.post("/ask")
def ask(q: Query):
    return {"response": run_agents(q)}