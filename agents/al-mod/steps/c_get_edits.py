import dspy
from pydantic import BaseModel
from .b_get_relevant_locations import ProblemLocation

class SearchReplaceEdit(BaseModel):
  """
  The *SEARCH/REPLACE* edit must use this format:
  1. The start of search block: <<<<<<< SEARCH
  2. A contiguous chunk of lines to search for in the existing source code
  3. The dividing line: =======
  4. The lines to replace into the source code
  5. The end of the replace block: >>>>>>> REPLACE
  
  Here is an example:
  ```python
  ### mathweb/flask/app.py
  <<<<<<< SEARCH
  from flask import Flask
  =======
  import math
  from flask import Flask
  >>>>>>> REPLACE
  ```
  
  Please note that the *SEARCH/REPLACE* edit REQUIRES PROPER INDENTATION. If you would like to add the line '        print(x)', you must fully write that out, with all those spaces before the code!
  Wrap the *SEARCH/REPLACE* edit in blocks ```python...```.
  """
  full_file_path: str
  search_replace_edit: str
  

class GithubRepoIssueSolution(dspy.Signature):
  """
  Localize the bug based on the problem description, and then generate a comprehensive set of *SEARCH/REPLACE* edits to fix the issue.
  """
  
  github_problem_description: str = dspy.InputField()
  skeleton_of_relevant_files: str = dspy.InputField()
  potential_problem_locations: list[ProblemLocation] = dspy.InputField()
  edits: list[SearchReplaceEdit] = dspy.OutputField()
  
c = dspy.ChainOfThought(GithubRepoIssueSolution)
