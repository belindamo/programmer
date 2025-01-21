import os
from dotenv import load_dotenv
import dspy
import json
load_dotenv()

lm = dspy.LM('openai/gpt-4o-mini', api_key=os.getenv('API_KEY'), api_base=os.getenv('API_BASE'))
dspy.configure(lm=lm)

def dummy(task_data):

  dummy = dspy.ChainOfThought("issue -> patch: str")
  return dummy(issue=f"""You are a skilled software engineer. Provide patches in git diff format.

Given this GitHub issue:
{task_data['issue_text']}

Base commit: {task_data['base_commit']}
Files to modify: {', '.join(task_data['file_paths'])}

Additional context: {json.dumps(task_data['context'], indent=2)}

Please provide a patch in git diff format that resolves this issue.
The patch should be applicable to the base commit.
Only include the git diff, no additional explanation.""")

if __name__ == "__main__":
  dummy()