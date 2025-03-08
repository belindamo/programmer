"""Get the folder structure in a string, given a folder path, with AI-generated descriptions"""

import os
from .ai import ai
import html
from typing import Optional
import re

# Paths to ignore
IGNORE_PATHS = {
  # Default folders
  "__pycache__",
  "scratch",
  ".git",
  # Common file patterns
  "*.pyc",
  "*.pyo",
  "*.pyd",
  ".DS_Store"
}

def escape_xml(text: str) -> str:
  """Escape special characters for XML"""
  return html.escape(text, quote=True)

class NLDirectory:
  """Natural language directory class for getting folder structure with brief LLM-generated file descriptions"""
  
  def __init__(self, root_path: str, max_depth: Optional[int] = None, structure: Optional[str] = None):
    """Initialize NLDirectory
    
    Args:
      root_path (str): Path to folder to analyze
      max_depth (int, optional): Maximum depth of directory traversal.
                               0 means only immediate children.
                               None means no limit. Defaults to None.
      structure (str, optional): Pre-existing directory structure in XML format.
                               If provided, skips the directory scanning process.
    """
    self.root_path = root_path
    self.max_depth = max_depth
    
    # If structure is provided, use it directly
    if structure is not None:
      self.structure = structure
      return
    
    # Start with default ignore paths
    self.ignore_paths = set(IGNORE_PATHS)
    
    # Add patterns from .gitignore if it exists
    gitignore_path = os.path.join(root_path, '.gitignore')
    if os.path.exists(gitignore_path):
      with open(gitignore_path, 'r') as f:
        for line in f:
          line = line.strip()
          # Skip empty lines and comments
          if line and not line.startswith('#'):
            self.ignore_paths.add(line.strip('/'))
    
    self.structure = self.get_structure()
  
  def get_skeleton(self, file_paths: list[str]) -> str:
    """Get raw contents of specified files with structure information in XML format
    
    Args:
      file_paths (list[str]): List of file paths to get contents for
      
    Returns:
      str: Combined raw contents of all specified files with structure information in XML format
    """
    file_contents = {}
    file_structures = {}
    
    for file_path in file_paths:
      full_path = os.path.join(self.root_path, file_path)
      if os.path.exists(full_path) and os.path.isfile(full_path):
        try:
          with open(full_path, 'r') as f:
            content = f.read()
            file_contents[file_path] = content
            
            # Extract classes and functions
            classes = []
            functions = []
            
            # Simple parsing for Python files
            if file_path.endswith('.py'):
              lines = content.split('\n')
              current_class = None
              class_stack = []  # Stack to track nested classes
              function_stack = []  # Stack to track functions/methods
              
              for i, line in enumerate(lines):
                line_num = i + 1  # 1-indexed line numbers
                stripped_line = line.strip()
                indentation = len(line) - len(line.lstrip())
                
                # Skip empty lines and comments
                if not stripped_line or stripped_line.startswith('#'):
                  continue
                
                # Match class definitions
                class_match = re.match(r'^\s*class\s+(\w+)', line)
                if class_match:
                  class_name = class_match.group(1)
                  
                  # Close any functions at the same or higher indentation level
                  while function_stack and function_stack[-1]['indentation'] >= indentation:
                    func = function_stack.pop()
                    func['end_line'] = line_num - 1
                  
                  # Close any classes at the same indentation level
                  while class_stack and class_stack[-1]['indentation'] == indentation:
                    cls = class_stack.pop()
                    cls['end_line'] = line_num - 1
                  
                  new_class = {
                    'name': class_name,
                    'start_line': line_num,
                    'end_line': None,
                    'indentation': indentation,
                    'methods': []
                  }
                  
                  classes.append(new_class)
                  class_stack.append(new_class)
                  current_class = new_class
                
                # Match function/method definitions
                func_match = re.match(r'^\s*def\s+(\w+)', line)
                if func_match:
                  func_name = func_match.group(1)
                  
                  # Close any functions at the same or higher indentation level
                  while function_stack and function_stack[-1]['indentation'] >= indentation:
                    func = function_stack.pop()
                    func['end_line'] = line_num - 1
                  
                  # Determine if this is a method or a standalone function
                  is_method = False
                  for cls in reversed(class_stack):
                    if indentation > cls['indentation']:
                      is_method = True
                      method = {
                        'name': func_name,
                        'start_line': line_num,
                        'end_line': None,
                        'indentation': indentation
                      }
                      cls['methods'].append(method)
                      function_stack.append(method)
                      break
                  
                  if not is_method:
                    # This is a standalone function
                    func = {
                      'name': func_name,
                      'start_line': line_num,
                      'end_line': None,
                      'indentation': indentation,
                      'file': file_path
                    }
                    functions.append(func)
                    function_stack.append(func)
              
              # Close any remaining open functions and classes
              for func in function_stack:
                func['end_line'] = len(lines)
              
              for cls in class_stack:
                cls['end_line'] = len(lines)
            
            # Clean up the structures by removing temporary fields
            for cls in classes:
              if 'indentation' in cls:
                del cls['indentation']
              for method in cls['methods']:
                if 'indentation' in method:
                  del method['indentation']
            
            for func in functions:
              if 'indentation' in func:
                del func['indentation']
            
            file_structures[file_path] = {
              'classes': classes,
              'functions': functions
            }
            
        except Exception as e:
          print(f"Error reading file {file_path}: {str(e)}")
          file_contents[file_path] = f"# Error reading file: {str(e)}"
          file_structures[file_path] = {'classes': [], 'functions': []}
    
    # Format the content with file paths and structure information in XML
    output = ['<files>']
    output.append("<files>")
    
    for file_path, content in file_contents.items():
      structure = file_structures[file_path]
      
      # Start file tag
      output.append(f'  <file path="{escape_xml(file_path)}">')
      
      # Add structure information
      if structure['classes'] or structure['functions']:
        output.append('    <structure>')
        
        # Add classes
        for cls in structure['classes']:
          output.append(f'      <class name="{escape_xml(cls["name"])}" start_line="{cls["start_line"]}" end_line="{cls["end_line"]}">')
          for method in cls['methods']:
            output.append(f'        <method name="{escape_xml(method["name"])}" start_line="{method["start_line"]}" end_line="{method["end_line"]}" />')
          output.append('      </class>')
        
        # Add functions
        for func in structure['functions']:
          output.append(f'      <function name="{escape_xml(func["name"])}" start_line="{func["start_line"]}" end_line="{func["end_line"]}" />')
        
        output.append('    </structure>')
      
      # Add file content with proper CDATA handling
      # CDATA sections can't contain the sequence ']]>', so we need to split and rejoin if it exists
      output.append('    <content><![CDATA[')
      # Replace any ']]>' in the content with ']]]]><![CDATA[>' to properly escape it in CDATA
      safe_content = content.replace(']]>', ']]]]><![CDATA[>')
      output.append(safe_content)
      output.append('    ]]></content>')
      
      # Close file tag
      output.append('  </file>')
    
    output.append("</files>")
    return "\n".join(output)
  
  def get_structure(self) -> str:
    """Get folder structure with AI descriptions in XML format
    
    Returns:
      str: XML string containing folder structure with descriptions
    """
    print(f"Starting to process directory: {self.root_path}")
    print(f"Max depth: {self.max_depth}")
    print(f"Ignore patterns: {self.ignore_paths}")
    
    output = ["<directory>"]
    
    def process_dir(path: str, level: int = 0) -> None:
      if self.max_depth is not None and level > self.max_depth:
        print(f"Reached max depth {self.max_depth}, stopping at {path}")
        return

      print(f"\nProcessing directory at level {level}: {path}")
      indent = "  " * (level + 1)
      
      # Process files first
      for file in os.listdir(path):
        file_path = os.path.join(path, file)
        rel_path = os.path.relpath(file_path, self.root_path)
        
        # Check if path should be ignored
        should_ignore = False
        for ignore_pattern in self.ignore_paths:
          if '*' in ignore_pattern:
            # Handle wildcard patterns
            pattern = ignore_pattern.replace('*', '')
            if rel_path.endswith(pattern):
              print(f"Ignoring {rel_path} - matches wildcard pattern {ignore_pattern}")
              should_ignore = True
              break
          elif ignore_pattern in rel_path:
            print(f"Ignoring {rel_path} - matches pattern {ignore_pattern}")
            should_ignore = True
            break
        
        if should_ignore:
          continue
        
        if os.path.isfile(file_path):
          print(f"Processing file: {rel_path}")
          with open(file_path, "r") as f:
            try:
              content = f.read()
              print(f"Successfully read file content for {rel_path}")
            except Exception as e:
              print(f"Error reading file {rel_path}: {str(e)}")
              content = ""
          print(f"Getting AI description for {rel_path}")
          description = ai(
            "You are a helpful assistant that writes 1 sentence summaries of files.",
            f"File: {rel_path}\n\nSummarize this file in 1 sentence: {content}",
          )
          output.append(
            f'{indent}<file name="{escape_xml(file)}" description="{escape_xml(description)}" />'
          )

      # Then process subdirectories  
      for item in os.listdir(path):
        item_path = os.path.join(path, item)
        rel_path = os.path.relpath(item_path, self.root_path)
        
        # Check if path should be ignored
        should_ignore = False
        for ignore_pattern in self.ignore_paths:
          if '*' in ignore_pattern:
            pattern = ignore_pattern.replace('*', '')
            if rel_path.endswith(pattern):
              print(f"Ignoring directory {rel_path} - matches wildcard pattern {ignore_pattern}")
              should_ignore = True
              break
          elif ignore_pattern in rel_path:
            print(f"Ignoring directory {rel_path} - matches pattern {ignore_pattern}")
            should_ignore = True
            break
        
        if should_ignore:
          continue
        
        if os.path.isdir(item_path):
          print(f"Processing subdirectory: {rel_path}")
          output.append(f'{indent}<folder name="{escape_xml(item)}">')
          process_dir(item_path, level + 1)
          output.append(f"{indent}</folder>")

    process_dir(self.root_path)
    output.append("</directory>")
    print("\nFinished processing directory structure")
    return "\n".join(output)

if __name__ == "__main__":
  # Create directory object and print XML structure
  dir_obj = NLDirectory("envs/kg-gen-c88908c")
  print(dir_obj.structure)
