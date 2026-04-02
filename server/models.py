from pydantic import BaseModel
from typing import List, Optional, Literal


class Observation(BaseModel):
    visible_features: List[str]
    revealed_issues: List[str]
    revealed_signals: List[str]
    remaining_budget: int
    difficulty: str
    current_step: int = 0
    max_steps: int = 4
    can_submit: bool = False


class Action(BaseModel):
    action_type: Literal[
        "inspect_tests",
        "inspect_docs",
        "inspect_docker",
        "inspect_popularity",
        "submit_final"
    ]
    score: Optional[float] = None
    feedback: Optional[str] = None


class Reward(BaseModel):
    value: float