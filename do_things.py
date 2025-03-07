import argparse
import json
import importlib
from pathlib import Path
from tasks.models import Task

if __name__ == "__main__":
  # Parse command line arguments
  parser = argparse.ArgumentParser()
  parser.add_argument("--agent", required=True, help="Name of agent folder")
  parser.add_argument("--tasks", required=True, help="Name of tasks file")
  args = parser.parse_args()

  # Import the agent's main function
  try:
    agent_module = importlib.import_module(f"agents.{args.agent}.main")
    agent_main = agent_module.main
  except ImportError as e:
    print(f"Could not import agent {args.agent}: {e}")
  except AttributeError:
    print(f"Agent {args.agent} does not have a main() function")

  # Load tasks from jsonl file
  tasks_file = Path("tasks") / args.tasks
  if not tasks_file.exists():
    print(f"Tasks file {tasks_file} does not exist")

  # Process each task
  with open(tasks_file) as f:
    for line in f:
      if not line.strip():
        continue
      try:
        task_dict = json.loads(line)
        task = Task(**task_dict)
        agent_main(task)
      except json.JSONDecodeError:
        print(f"Invalid JSON in line: {line}")
      except Exception as e:
        print(f"Error processing task: {e}")