from pydantic import BaseModel

class Task(BaseModel):
  problem: str
  env: str
