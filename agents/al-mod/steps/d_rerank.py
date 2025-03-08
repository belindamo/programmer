import json
import os
import re
from collections import Counter
from typing import List, Dict, Tuple, Any, Optional

from ..steps.c_get_edits import SearchReplaceEdit


def extract_search_replace_content(edit_text: str) -> Tuple[str, str]:
    """
    Extract the search and replace content from a search/replace edit.
    
    Args:
        edit_text: The search/replace edit text
        
    Returns:
        Tuple of (search_content, replace_content)
    """
    search_pattern = r'<<<<<<< SEARCH\n(.*?)\n=======\n'
    replace_pattern = r'=======\n(.*?)\n>>>>>>> REPLACE'
    
    search_match = re.search(search_pattern, edit_text, re.DOTALL)
    replace_match = re.search(replace_pattern, edit_text, re.DOTALL)
    
    search_content = search_match.group(1) if search_match else ""
    replace_content = replace_match.group(1) if replace_match else ""
    
    return search_content, replace_content


def remove_comments_and_whitespace(code: str) -> str:
    """
    Remove comments and normalize whitespace in code.
    This is a simplified version of the reference implementation.
    
    Args:
        code: The code to normalize
        
    Returns:
        Normalized code
    """
    # Remove Python comments
    code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
    
    # Remove empty lines
    code = re.sub(r'\n\s*\n', '\n', code)
    
    # Normalize whitespace
    code = re.sub(r'\s+', ' ', code)
    
    return code.strip()


# Helper function to normalize a patch
def normalize_patch(edit: SearchReplaceEdit) -> str:
    """
    Normalize a patch by removing whitespace, comments, and other non-essential differences.
    This helps with deduplication and voting.
    """
    try:
        # Extract search and replace content
        search_content, replace_content = extract_search_replace_content(edit.search_replace_edit)
        
        # Normalize the search and replace content
        normalized_search = remove_comments_and_whitespace(search_content)
        normalized_replace = remove_comments_and_whitespace(replace_content)
        
        # Combine the normalized content
        normalized = f"SEARCH:{normalized_search}|REPLACE:{normalized_replace}"
        
        # Log the normalization for debugging
        print(f"DEBUG - Normalizing patch for file: {edit.full_file_path}")
        print(f"DEBUG - Original length: {len(edit.search_replace_edit)}, Normalized length: {len(normalized)}")
        
        return normalized
    except Exception as e:
        print(f"ERROR - Failed to normalize patch: {e}")
        # Fall back to simple normalization
        return edit.search_replace_edit.strip()


# Class to handle JSON encoding of sets
class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def normalize_samples(samples: List[List[SearchReplaceEdit]]) -> List[Dict[str, Any]]:
    """
    Normalize all samples.
    
    Args:
        samples: List of sample edits, where each sample is a list of SearchReplaceEdit objects
        
    Returns:
        List of normalized samples with their metadata
    """
    normalized_samples = []
    
    print(f"DEBUG - Normalizing {len(samples)} samples")
    
    for i, sample in enumerate(samples):
        print(f"DEBUG - Sample {i} has {len(sample)} edits")
        
        # Normalize each edit in the sample
        normalized_edits = []
        for edit in sample:
            normalized_patch = normalize_patch(edit)
            normalized_edits.append({
                "normalized_patch": normalized_patch,
                "patch": edit.search_replace_edit,
                "full_file_path": edit.full_file_path
            })
        
        # Create a combined normalized representation of the entire sample
        # This is used for voting
        combined_normalized = "|".join(sorted([e["normalized_patch"] for e in normalized_edits]))
        
        normalized_samples.append({
            "sample_id": i,
            "normalized_sample": combined_normalized,
            "edits": sample,  # Keep the original edits
            "normalized_edits": normalized_edits  # Store normalized edits for debugging
        })
    
    return normalized_samples


def majority_voting(normalized_samples: List[Dict[str, Any]]) -> List[SearchReplaceEdit]:
    """
    Perform majority voting on the normalized samples.
    
    Args:
        normalized_samples: List of normalized samples with their metadata
        
    Returns:
        List of SearchReplaceEdit objects from the winning sample
    """
    print(f"DEBUG - Performing majority voting on {len(normalized_samples)} samples")
    
    if not normalized_samples:
        return []
    
    # Count votes for each normalized sample
    vote = Counter()
    first_appear_idx = {}
    
    for sample in normalized_samples:
        sample_key = sample["normalized_sample"]
        if sample_key.strip():
            vote[sample_key] += 1
            if sample_key not in first_appear_idx:
                first_appear_idx[sample_key] = sample["sample_id"]
    
    print(f"DEBUG - Vote counts: {dict(vote)}")
    
    # Find the majority vote
    if not vote:
        return []
    
    # Get the sample with the most votes
    # If there's a tie, choose the one that appeared first
    majority_sample_key = max(vote.keys(), key=lambda k: (vote[k], -first_appear_idx[k]))
    majority_sample_id = first_appear_idx[majority_sample_key]
    
    print(f"DEBUG - Majority vote: Sample {majority_sample_id} with {vote[majority_sample_key]} votes")
    
    # Return the edits from the winning sample
    for sample in normalized_samples:
        if sample["sample_id"] == majority_sample_id:
            return sample["edits"]
    
    # This should never happen
    return []


def d(samples: Optional[List[List[SearchReplaceEdit]]] = None) -> List[SearchReplaceEdit]:
    """
    Main reranking function.
    
    Args:
        samples: List of sample edits, where each sample is a list of SearchReplaceEdit objects.
                If None, this function will be a no-op and return an empty list.
    
    Returns:
        List of SearchReplaceEdit objects from the winning sample
    """
    if samples is None:
        print("No samples provided for reranking.")
        return []
    
    print("\n=== Reranking Edits ===")
    print(f"DEBUG - Received {len(samples)} samples for reranking")
    
    # Check if samples is empty
    if len(samples) == 0:
        print("WARNING: Empty samples list provided for reranking.")
        return []
    
    # Check the structure of the samples
    print(f"DEBUG - First sample has {len(samples[0])} edits")
    
    # Normalize samples
    normalized_samples = normalize_samples(samples)
    
    # Perform majority voting at the sample level
    reranked_edits = majority_voting(normalized_samples)
    
    print(f"Reranked to select the best sample with {len(reranked_edits)} edits.")
    
    # Print the reranked edits
    for i, edit in enumerate(reranked_edits):
        print(f"\nReranked Edit {i + 1}:")
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
    
    return reranked_edits
