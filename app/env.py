import random
import json
from app.models import Observation, Action
from app.grader import reward_fn


class HackathonEnv:
    def __init__(self):
        with open("app/dataset.json") as f:
            self.data = json.load(f)

        self.current = None
        self.done = False
        self.last_reward = 0

    def reset(self, difficulty=None):
        """
        Start a new episode
        """
        if difficulty:
            filtered = [x for x in self.data if x["difficulty"] == difficulty]
            self.current = random.choice(filtered)
        else:
            self.current = random.choice(self.data)

        self.done = False
        return self._get_obs()

    def step(self, action: Action):
        """
        Take an action and return (obs, reward, done, info)
        """
        if self.done:
            raise Exception("Episode already finished. Call reset().")

        true_score = self.current["true_score"]
        issues = self.current["issues"]

        reward = reward_fn(
            pred_score=action.score,
            true_score=true_score,
            feedback=action.feedback,
            issues=issues,
            difficulty=self.current["difficulty"]
        )

        self.last_reward = reward
        self.done = True

        return self._get_obs(), reward, self.done, {}

    def state(self):
        """
        Return full internal state (for debugging)
        """
        return self.current

    def _get_obs(self):
        """
        Convert internal state to Observation
        """
        return Observation(
            features=self.current["features"],
            has_tests=self.current["has_tests"],
            has_docs=self.current["has_docs"],
            has_docker=self.current["has_docker"],
            stars=self.current["stars"],
            difficulty=self.current["difficulty"]
        )