import dspy

class RelevantFiles(dspy.Signature):
  """Extract top file paths that might be relevant or need to be edited to fix a given problem."""

  repository_structure: str = dspy.InputField()
  github_problem_description: str = dspy.InputField()
  full_paths: list[str] = dspy.OutputField(desc="in decreasing importance, files to be edited")
  
a = dspy.ChainOfThought(RelevantFiles)