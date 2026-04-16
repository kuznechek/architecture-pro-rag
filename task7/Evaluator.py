import json
import time
import requests
from datetime import datetime

class Evaluator:
    def __init__(self, api_url="http://localhost:8001/ask", questions_file="golden_set.json", log_file="evaluation_log.jsonl"):
        self.api_url = api_url
        self.questions_file = questions_file
        self.log_file = log_file

    def _load_questions(self):
        with open(self.questions_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _evaluate_response(self, question_data, response_data):
        category = question_data.get("category")
        
        has_chunks = response_data.get("num_sources", 0) > 0
        response_text = response_data.get("response", "")
        
        if category == "known":
            success = has_chunks and len(response_text) > 0
            completeness = "good" if success and len(response_text) > 50 else "partial" if success else "none"
        elif category == "absent":
            no_info_phrases = ["не нашёл", "не найдено", "no information", "not found", "извините"]
            has_no_info = any(phrase in response_text.lower() for phrase in no_info_phrases)
            success = (not has_chunks) or has_no_info
            completeness = "good" if success else "bad"
        else:
            success = False
            completeness = "unknown"
        
        return {
            "success": success,
            "completeness": completeness,
            "has_chunks": has_chunks,
            "response_length": len(response_text)
        }

    def run(self):
        questions = self._load_questions()
        
        with open(self.log_file, "a", encoding="utf-8") as log_f:
            for idx, q in enumerate(questions, 1):
                print(f"Processing {idx}/{len(questions)}: {q['question']}")
                payload = {
                    "question": q["question"],
                    "prompt_type": "base"
                }
                
                resp = None
                data = {}
                elapsed = None
                
                try:
                    start = time.time()
                    resp = requests.post(self.api_url, json=payload, timeout=60)
                    elapsed = time.time() - start
                    
                    if resp.status_code == 200:
                        data = resp.json()
                except Exception as e:
                    evaluation = {
                        "success": False,
                        "completeness": "exception",
                        "has_chunks": False,
                        "response_length": 0
                    }
                    response_text = str(e)
                    
                    log_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "question": q["question"],
                        "category": q.get("category", "unknown"),
                        "response": response_text[:500],
                        "num_sources": 0,
                        "sources": [],
                        "evaluation": evaluation,
                        "elapsed_seconds": None
                    }
                    log_f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                    log_f.flush()
                    time.sleep(1)
                    continue
                
                if resp and resp.status_code == 200:
                    if "error" in data:
                        evaluation = {
                            "success": False,
                            "completeness": "error",
                            "has_chunks": False,
                            "response_length": 0
                        }
                        response_text = data["error"]
                    else:
                        evaluation = self._evaluate_response(q, data)
                        response_text = data.get("response", "")
                else:
                    evaluation = {
                        "success": False,
                        "completeness": "http_error",
                        "has_chunks": False,
                        "response_length": 0
                    }
                    response_text = f"HTTP {resp.status_code if resp else 'no response'}"
                    data = {}

                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "question": q["question"],
                    "category": q.get("category", "unknown"),
                    "response": response_text[:500],
                    "num_sources": data.get("num_sources", 0) if resp and resp.status_code == 200 and "error" not in data else 0,
                    "sources": data.get("sources", [])[:5],
                    "evaluation": evaluation,
                    "elapsed_seconds": round(elapsed, 2) if elapsed else None
                }
                log_f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                log_f.flush()
                time.sleep(1)

        print(f"Evaluation completed. Log saved to {self.log_file}")