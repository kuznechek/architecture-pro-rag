from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from RAGBot import RAGBot
import traceback
import os

app = FastAPI(title="RAGBot API")

bot = RAGBot(setup_dir="/app")

class QueryRequest(BaseModel):
    question: str
    prompt_type: str = "base"

class QueryResponse(BaseModel):
    query: str
    prompt_type: str
    response: str
    sources: list
    num_sources: int

@app.post("/ask", response_model=QueryResponse)
async def ask(request: QueryRequest):
    try:
        result = bot.ask(request.question, request.prompt_type)
        return result
    except Exception as e:
        error_detail = traceback.format_exc()
        print(error_detail)
        return {"error": str(e), "trace": error_detail}

@app.get("/health")
async def health():
    return {"status": "ok"}
    
@app.get("/test")
async def test():
    try:
        result = bot.ask("Who is Sauron?", "base")
        return {"status": "ok"}
    except Exception as e:
        error_detail = traceback.format_exc()
        print(error_detail)
        return {"error": str(e), "trace": error_detail}