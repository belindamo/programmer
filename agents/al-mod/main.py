from tasks.models import Task
from .steps.a_get_relevant_files import a
from .steps.b_get_relevant_locations import b, ProblemLocation 
from .steps.c_get_edits import c, SearchReplaceEdit
from .steps.d_rerank import d
from .utils.directory import NLDirectory
import os
import dspy
from concurrent.futures import ThreadPoolExecutor
from typing import List

N_SAMPLES = 8

def main(task: Task) -> None:
  print(f"AL-MOD agent processing task:")
  print(f"- Problem: {task.problem}")
  print(f"- Environment: {task.env}")
  
  gpt4o = dspy.LM("openai/gpt-4o", temperature=0)
  dspy.configure(lm=gpt4o)

  problem = task.problem
  env = task.env

  # Check for cached directory structure
  directory = None
  cache_path = os.path.join(os.path.dirname(__file__), 'dir_caches', f'{env}.xml')
  if os.path.exists(cache_path):
    print(f"Using cached directory structure from {cache_path}")
    with open(cache_path, 'r') as f:
      directory_str = f.read()
    # Create NLDirectory with the cached structure
    directory = NLDirectory(f'envs/{env}', structure=directory_str)
  else:
    # Create NLDirectory and generate the structure
    directory = NLDirectory(f'envs/{env}')
  
  relevant_files: list[str] = a(
    repository_structure=directory.structure,
    github_problem_description=problem, 
  ).full_paths
  # print('RELEVANT FILES', relevant_files)
  
  relevant_files_skeleton: str = directory.get_skeleton(relevant_files)
  # print('RELEVANT FILES SKELETON:', relevant_files_skeleton)
  
  potential_problem_locations: list[ProblemLocation] = b(
    github_problem_description=problem,
    skeleton_of_relevant_files=relevant_files_skeleton # TODO improve get_skeleton
  ).locations
  print('POTENTIAL PROBLEM LOCATIONS:', potential_problem_locations)

  gpt4o_with_temp = dspy.LM("openai/gpt-4o", temperature=0.9, cache=False)
  dspy.configure(lm=gpt4o_with_temp)

  def generate_sample(args) -> List[SearchReplaceEdit]:
    problem, skeleton, locations = args
    try:
      return c(
        github_problem_description=problem,
        skeleton_of_relevant_files=skeleton, 
        potential_problem_locations=locations
      ).edits
    except Exception as e:
      print(f"Failed to generate sample: {e}")
      return None
  
  samples = []
  with ThreadPoolExecutor(max_workers=16) as executor:
    args = [(problem, relevant_files_skeleton, potential_problem_locations)] * N_SAMPLES
    for result in executor.map(generate_sample, args):
      if result is not None:
        samples.append(result)
        print('SAMPLE', result)
  
  # Rerank the samples and get the best one
  reranked_edits = d(samples)
  
  print("\n=== Top Ranked Sample ===")
  if reranked_edits:
    for i, edit in enumerate(reranked_edits):
      print(f"\nEdit {i + 1}:")
      print(f"File: {edit.full_file_path}")
      print("Edit:")
      # Pretty print the search/replace blocks
      lines = edit.search_replace_edit.split('\n')
      in_code_block = False
      for line in lines:
        if line.startswith('```'):
          in_code_block = not in_code_block
          continue
        if line.startswith('###'):
          print('\n' + line)
          continue
        if '<<<<<<< SEARCH' in line:
          print('\n' + line)
          continue
        if '=======' in line:
          print(line)
          continue  
        if '>>>>>>> REPLACE' in line:
          print(line)
          continue
        if in_code_block:
          print('  ' + line)
      print("-" * 50)
  else:
    print("No edits were found after reranking.")
  
  # Return the reranked edits
  return reranked_edits
    
    
if __name__ == "__main__":
  task = Task(
    problem="the cluster=True is returning an error. Fix the issues identified here",
    # problem="remove clustering functionality altogether",
    env="kg-gen-c88908c"
  )
  main(task)

