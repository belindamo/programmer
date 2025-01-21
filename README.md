# Programmer: a LLM-based system that codes

This system is benchmarked on SWE-bench. 

## Getting started

- Clone `.env.example` into `.env` and fill in your keys and urls
- Run `poetry install`
- Run `poetry run python -m main`

## Files

Important files and folders
- `main.py`: main entry point to run
- `steps/` folder: steps taken to solve an issue
- `.txt` files: are the ids of SWE-bench instances
- `output_preds/` folder: where the generated patches are saved, alongside other systems' outputs for comparison

## Steps

1. Get 4 sets of edit locations
2. For each set, generate 16 patches: 15 by temperature sampling and 1 greedy
3. Of the 64 patches, select by majority vote the best 1

After this, we'll want to add validation via regression testing.