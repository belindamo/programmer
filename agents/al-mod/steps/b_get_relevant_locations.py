import dspy
from typing import Literal
from pydantic import BaseModel

class CodeLocation(BaseModel):
  kind: Literal['variable', 'function', 'class', 'method']
  name: str

class ProblemLocation(BaseModel):
  full_file_path: str 
  code_locations: list[CodeLocation]
  
class RelevantProblemLocations(dspy.Signature):
  """
  Identify all locations (i.e. global variables, functions, classes, and/or methods) that need inspection or editing to fix the problem below. If you include a class, you do not need to also list its specific methods.
  
  List locations by relevant file. In each file, enumerate each identifier (and its kind) for inspection.
  """
  
  github_problem_description: str = dspy.InputField()
  skeleton_of_relevant_files: str = dspy.InputField()
  locations: list[ProblemLocation] = dspy.OutputField()
  
b = dspy.ChainOfThought(RelevantProblemLocations)