from dspy import dspy

#
##
### ~~~ LOCALIZE ~~~ ###
##
#

relevant_files_desc = """Look through the following GitHub problem description and Repository structure and provide a list of files that one would need to edit to fix the problem.

Please only provide the full path and return at most 5 files. The returned files should be separated by new lines ordered by most to least important and wrapped with ```

For example:
```
file1.py
file2.py
```
"""

class RelevantFiles(dspy.Signature):
  f"""{relevant_files_desc}"""
  
  github_problem_description: str = dspy.InputField()
  repository_structure: str = dspy.InputField()
  files: str = dspy.OutputField()
  

relevant_problem_locations_desc = """Look through the following GitHub Problem Description and the Skeleton of Relevant Files.
Identify all locations that need inspection or editing to fix the problem, including directly related areas as well as any potentially related global variables, functions, and classes.
For each location you provide, either give the name of the class, the name of a method in a class, the name of a function, or the name of a global variable.

Please provide the complete set of locations as either a class name, a function name, or a variable name.
Note that if you include a class, you do not need to list its specific methods.
You can include either the entire class or don't include the class name and instead include specific methods in the class.
### Examples:
```
full_path1/file1.py
function: my_function_1
class: MyClass1
function: MyClass2.my_method

full_path2/file2.py
variable: my_var
function: MyClass3.my_method

full_path3/file3.py
function: my_function_2
function: my_function_3
function: MyClass4.my_method_1
class: MyClass5
```

Return just the locations.
"""

class RelevantProblemLocations(dspy.Signature):
  __doc__ = relevant_problem_locations_desc
  
  github_problem_description: str = dspy.InputField()
  skeleton_of_relevant_files: str = dspy.InputField()
  locations: str = dspy.OutputField()


relevant_code_with_lines_desc = """Please review the following GitHub problem description and relevant files, and provide a set of locations that need to be edited to fix the issue.
The locations can be specified as class names, function or method names, or exact line numbers that require modification.

Please provide the class name, function or method name, or the exact line numbers that need to be edited.
### Examples:
```
full_path1/file1.py
line: 10
class: MyClass1
line: 51

full_path2/file2.py
function: MyClass2.my_method
line: 12

full_path3/file3.py
function: my_function
line: 24
line: 156
```

Return just the location(s)
"""
# line number
class RelevantCodeWithLines(dspy.Signature):
  __doc__ = relevant_code_with_lines_desc
  
  github_problem_description: str = dspy.InputField()
  relevant_files: str = dspy.InputField()
  locations: str = dspy.OutputField()


relevant_code_desc = """Please review the following GitHub problem description and relevant files, and provide a set of locations that need to be edited to fix the issue.
The locations can be specified as class, method, or function names that require modification.

Please provide the class, method, or function names that need to be edited.
### Examples:
```
full_path1/file1.py
function: my_function1
class: MyClass1

full_path2/file2.py
function: MyClass2.my_method
class: MyClass3

full_path3/file3.py
function: my_function2
```

Return just the location(s)
"""

class RelevantCode(dspy.Signature):
  __doc__ = relevant_code_desc
  
  github_problem_description: str = dspy.InputField()
  relevant_files: str = dspy.InputField()
  locations: str = dspy.OutputField()


#
##
### ~~~ REPAIR ~~~ ###
##
#

# This uses repair_prompt_combine_topn_cot_diff. There are 3 original prompts, but we use the one that is used in the tutorial
github_repo_issue_solution_desc = """
We are currently solving an issue within our repository. You are given the Github issue and code segments from relevant files. One or more of these files may contain bugs. 

Please first localize the bug based on the issue statement, and then generate *SEARCH/REPLACE* edits to fix the issue.

Every *SEARCH/REPLACE* edit must use this format:
1. The file path
2. The start of search block: <<<<<<< SEARCH
3. A contiguous chunk of lines to search for in the existing source code
4. The dividing line: =======
5. The lines to replace into the source code
6. The end of the replace block: >>>>>>> REPLACE

Here is an example:

```python
### mathweb/flask/app.py
from flask import Flask
```

Please note that the *SEARCH/REPLACE* edit REQUIRES PROPER INDENTATION. If you would like to add the line '        print(x)', you must fully write that out, with all those spaces before the code!
Wrap the *SEARCH/REPLACE* edit in blocks ```python...```.
"""

class GithubRepoIssueSolution(dspy.Signature):
  __doc__ = github_repo_issue_solution_desc
  
  github_issue: str = dspy.InputField()
  relevant_files: str = dspy.InputField()
  edits: str = dspy.OutputField()