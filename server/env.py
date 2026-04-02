import random
import json
import os
from server.models import Observation, Action
from server.grader import reward_fn
from server.tasks import TASKS


class HackathonEnv:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "dataset.json")

        if os.path.exists(data_path):
            with open(data_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = []

        self.current = None
        self.done = False
        self.last_reward = 0.0
        self.max_steps = 3
        self.current_step = 0

    def reset(self, difficulty=None):
        if difficulty is None:
            difficulty = random.choice(["easy", "medium", "hard"])

        try:
            if difficulty in TASKS and len(TASKS[difficulty]) > 0:
                self.current = random.choice(TASKS[difficulty])
            else:
                filtered = [x for x in self.data if x.get("difficulty") == difficulty]
                if filtered:
                    self.current = random.choice(filtered)
                elif self.data:
                    self.current = random.choice(self.data)
                else:
                    raise ValueError("No tasks available")

            self.current["difficulty"] = difficulty

        except Exception:
            self.current = {
                "features": [],
                "has_tests": False,
                "has_docs": False,
                "has_docker": False,
                "stars": 0,
                "difficulty": difficulty,
                "true_score": 0.0,
                "issues": []
            }

        self.done = False
        self.last_reward = 0.0
        self.current_step = 0
        return self._get_obs()

    def step(self, action: Action):
        if self.current is None:
            raise Exception("Environment not initialized. Call /reset first.")

        if self.done:
            raise Exception("Episode already finished. Call reset().")

        true_score = self.current.get("true_score", 0.0)
        issues = self.current.get("issues", [])
        difficulty = self.current.get("difficulty", "easy")

        reward = reward_fn(
            pred_score=action.score,
            true_score=true_score,
            feedback=action.feedback,
            issues=issues,
            difficulty=difficulty
        )

        self.last_reward = reward
        self.current_step += 1

        if self.current_step >= self.max_steps:
            self.done = True
        else:
            self.done = False

        return self._get_obs(), reward, self.done, {
            "current_step": self.current_step,
            "max_steps": self.max_steps
        }

    def state(self):
        return self.current

    def _get_obs(self):
        return Observation(
            features=self.current.get("features", []),
            has_tests=self.current.get("has_tests", False),
            has_docs=self.current.get("has_docs", False),
            has_docker=self.current.get("has_docker", False),
            stars=self.current.get("stars", 0),
            difficulty=self.current.get("difficulty", "easy")
        )