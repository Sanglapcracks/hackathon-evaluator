import random
from copy import deepcopy
from server.models import Observation, Action
from server.grader import reward_fn
from server.tasks import TASKS
from server.tasks import get_task_by_id


class HackathonEnv:
    def __init__(self):
        self.current = None
        self.done = False
        self.last_reward = 0.0
        self.max_steps = 4
        self.current_step = 0

    def reset(self, difficulty=None, task_id=None):
        self.current_step = 0
        self.done = False
        self.last_reward = 0.0

        if task_id:
            task = get_task_by_id(task_id)
            if task is None:
                raise ValueError(f"Unknown task_id: {task_id}")
        self.current = deepcopy(task)
        return self._get_obs()

        if difficulty is None:
            difficulty = random.choice(["easy", "medium", "hard"])

        if difficulty in TASKS and len(TASKS[difficulty]) > 0:
            self.current = deepcopy(random.choice(TASKS[difficulty]))
        else:
            raise ValueError(f"No tasks available for difficulty: {difficulty}")

        return self._get_obs()

    def step(self, action: Action):
        if self.current is None:
            raise Exception("Environment not initialized. Call reset() first.")

        if self.done:
            raise Exception("Episode already finished. Call reset().")

        self.current_step += 1
        reward = 0.0

        if action.action_type in [
            "inspect_tests",
            "inspect_docs",
            "inspect_docker",
            "inspect_popularity",
        ]:
            evidence = self.current["hidden_evidence"].get(action.action_type)

            if evidence:
                signal = evidence["signal"]
                issue = evidence["issue"]

                if signal not in self.current["revealed_signals"]:
                    self.current["revealed_signals"].append(signal)
                    reward += 0.05
                else:
                    reward -= 0.02  # repeated inspection penalty

                if issue and issue not in self.current["revealed_issues"]:
                    self.current["revealed_issues"].append(issue)
                    reward += 0.10
            else:
                reward -= 0.05

        elif action.action_type == "submit_final":
            pred_score = action.score if action.score is not None else 0.0
            feedback = action.feedback if action.feedback is not None else ""

            reward = reward_fn(
                pred_score=pred_score,
                true_score=self.current.get("true_score", 0.0),
                feedback=feedback,
                issues=self.current.get("issues", []),
                difficulty=self.current.get("difficulty", "easy")
            )

            # bonus for gathering useful evidence before final submission
            num_signals = len(self.current["revealed_signals"])
            num_issues = len(self.current["revealed_issues"])

            if num_signals >= 2:
                reward += 0.05
            if num_issues >= 1:
                reward += 0.05

            # penalty for submitting too early with little evidence
            if num_signals == 0:
                reward -= 0.10

            reward = max(0.0, min(1.0, reward))
            self.done = True

        else:
            reward -= 0.05

        if self.current_step >= self.max_steps and not self.done:
            self.done = True

        self.last_reward = max(0.0, min(1.0, reward))

        return self._get_obs(), self.last_reward, self.done, {
            "current_step": self.current_step,
            "max_steps": self.max_steps,
            "revealed_issues": self.current["revealed_issues"],
            "revealed_signals": self.current["revealed_signals"]
        }

    def state(self):
        return self.current

    def _get_obs(self):
        remaining_budget = self.max_steps - self.current_step

        return Observation(
            visible_features=self.current.get("visible_features", []),
            revealed_issues=self.current.get("revealed_issues", []),
            revealed_signals=self.current.get("revealed_signals", []),
            remaining_budget=remaining_budget,
            difficulty=self.current.get("difficulty", "easy"),
            current_step=self.current_step,
            max_steps=self.max_steps,
            can_submit=self.current_step > 0
        )