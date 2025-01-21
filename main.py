import os
from dotenv import load_dotenv
import requests
import json
import dspy
from steps.localize import localize
from steps.repair import repair
from steps.test import test
from dummy import dummy
from evaluate import evaluate

load_dotenv()

lm = dspy.LM('openai/gpt-4o-mini', api_key=os.getenv('API_KEY'), api_base=os.getenv('API_BASE'))
dspy.configure(lm=lm)

def main(id_file_path: str):
  """Run evaluations for all ids in a given .txt file"""
  
  with open(id_file_path, 'r') as f:
    task_ids = [line.strip() for line in f] 
    
  for task_id in task_ids:
    print(f'Running task id {task_id}')
    
    task_data = requests.get(f"{os.getenv('EVAL_BASE')}/api/v1/tasks/{task_id}").json()
    
    print(f"\nTask {task_id} data:", json.dumps(task_data, indent=2))
    
    # dummy call
    dummy_response = dummy(task_data)
    # Get the response from the dummy function
    print(f"\nDummy response:\n{dummy_response}")
    patch = dummy_response.patch
  
    # # Pass input to each function
    # localize_result = localize(task_data)
    # repair_result = repair(localize_result)
    # patch = test(repair_result)

    # print("Localization result:", localize_result)
    # print("Repair result:", repair_result)
    # print("Test result:", patch)

    # evaluation_result = evaluate(task_id, patch)
    # print("\nEvaluation result:", json.dumps(evaluation_result.json(), indent=2))


if __name__ == "__main__":
  main('single_id.txt')