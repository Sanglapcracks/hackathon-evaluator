from pydantic import BaseModel
from typing import List


# What the agent sees
class Observation(BaseModel):
    features: List[str]
    has_tests: bool
    has_docs: bool
    has_docker: bool
    stars: int
    difficulty: str


# What the agent outputs
class Action(BaseModel):
    score: float   # must be between 0 and 1
    feedback: str  # explanation


# Reward returned by environment
class Reward(BaseModel):
    value: float