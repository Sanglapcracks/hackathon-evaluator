import requests


class HackathonEnvClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def reset(self, difficulty: str = None):
        params = {"difficulty": difficulty} if difficulty else {}
        resp = requests.get(f"{self.base_url}/reset", params=params, timeout=30)
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

    def grader(self):
        resp = requests.get(f"{self.base_url}/grader", timeout=30)
        resp.raise_for_status()
        return resp.json()