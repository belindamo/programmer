# Programmer

## Run an example
```python
poetry run python do_things.py --agent al-mod --tasks kg-gen-c88908c.jsonl
```

## Why Programmer is useful
This is a very simple playground to run an agent of your choice in a folder of your choice.

- `envs/`: every folder in `envs/` is an environment that the agent has access to.
- `agents/`: every folder in `agents/` is an agent. Every agent should have a `main.py` which should include a `main()` function entrypoint that takes in a Task.
- `tasks/`: every `.jsonl` in `tasks/` is a set of tasks. `tasks/models.py` contains the Task model. 

Run an agent in an environment on 1+ tasks: 
```python
poetry run python do_things.py --agent <agent_folder_name> --tasks <task_jsonl_name>
```

where `agent_folder_name` is the exact name of the subfolder in `agents/` and `task_jsonl_name` is the exact name of the `.jsonl` in `tasks/`, including the `.jsonl` extension. Note that every task requires specifying an `env`.

## Stack

- Python: for runtime
- Poetry: for Python package management
- DSPy: for structuring language model calls
- LiteLLM: via DSPy, for LLM routing

## Notes

This is meant to be kept super simple! 😌 🐈
