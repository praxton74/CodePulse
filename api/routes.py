from fastapi import FastAPI
from ingestion.pipeline import ingest
from pydantic import BaseModel
from ingestion.chat import ask_repo as ask
from agent.agent import run_agent
from typing import Optional
app = FastAPI()

class IngestRequest(BaseModel):
    github_url: str
    
class QueryRequest(BaseModel):
    repo_name: str
    question: str
    github_token: Optional[str] = None
    repo_full_name: Optional[str] = None

@app.post("/ingest")
async def ingest_repo(req: IngestRequest):
    result = ingest(req.github_url)
    return { "result": result }

@app.post("/chat")
async def chat(req: QueryRequest):
    answer = run_agent(req.repo_name, req.question, req.github_token)
    return {"answer": answer}
    