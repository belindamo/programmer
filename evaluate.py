import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

EVAL_BASE = os.getenv('EVAL_BASE')
        
def evaluate(task_id: str, prediction: str):
  return requests.post(
      f"{EVAL_BASE}/api/v1/evaluate",
      json={
          "task_id": task_id,
          "prediction": prediction
      }
  )

if __name__ == "__main__":
  evaluate()
  
  