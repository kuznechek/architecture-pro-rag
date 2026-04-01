import json
import os
import traceback
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from RAGBot import RAGBot
from Evaluator import Evaluator

app = FastAPI(title="RAGBot API")

bot = RAGBot(setup_dir="/app")

LOG_FILE = "/app/logs/query_log.jsonl"

def log_query(query_data: dict) -> None:
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(query_data, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Failed to write query log: {e}")

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

        timestamp = datetime.now().isoformat()
        has_chunks = result['num_sources'] > 0
        response_length = len(result['response'])
        success = (response_length > 0 and
                   not any(phrase in result['response'].lower()
                           for phrase in ["не нашёл", "не найдено", "извините", "no information"]))
        sources_list = [src.get('source', 'unknown') for src in result.get('sources', [])]

        log_data = {
            "timestamp": timestamp,
            "question": result['query'],
            "prompt_type": result['prompt_type'],
            "has_chunks": has_chunks,
            "response_length": response_length,
            "success": success,
            "sources": sources_list,
            "num_sources": result['num_sources']
        }
        log_query(log_data)

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
        evaluator = Evaluator()
        evaluator.run()
        return {"status": "evaluation_completed", "log_file": "evaluation_log.jsonl"}
    except Exception as e:
        error_detail = traceback.format_exc()
        print(error_detail)
        return {"error": str(e), "trace": error_detail}
