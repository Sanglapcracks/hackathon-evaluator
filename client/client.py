import requests


class HackathonEnvClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def reset(self, difficulty: str = None, task_id: str = None):
        payload = {}
        if difficulty:
            payload["difficulty"] = difficulty
        if task_id:
            payload["task_id"] = task_id

        resp = requests.post(f"{self.base_url}/reset", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def step(self, action: dict):
        resp = requests.post(f"{self.base_url}/step", json=action, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def state(self):
        resp = requests.get(f"{self.base_url}/state", timeout=30)
        resp.raise_for_status()
        return resp.json()

    def tasks(self):
        resp = requests.get(f"{self.base_url}/tasks", timeout=30)
        resp.raise_for_status()
        return resp.json()

    def baseline(self):
        resp = requests.get(f"{self.base_url}/baseline", timeout=30)
        resp.raise_for_status()
        return resp.json()

    def grader(self, task_id: str, score: float, feedback: str):
        resp = requests.post(
            f"{self.base_url}/grader",
            json={
                "task_id": task_id,
                "score": score,
                "feedback": feedback,
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()