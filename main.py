from fastapi import FastAPI
from app.env import HackathonEnv
from app.models import Action

app = FastAPI()

env = HackathonEnv()
def simple_policy(obs):
    score = 0.3

    if obs["has_tests"]:
        score += 0.2
    if obs["has_docs"]:
        score += 0.2
    if obs["has_docker"]:
        score += 0.2
    if obs["stars"] > 50:
        score += 0.1

    return {
        "score": min(score, 1),
        "feedback": "basic evaluation"
    }

@app.get("/")
def home():
    return {"message": "Hackathon Evaluator Environment Running"}


@app.get("/reset")
def reset(difficulty: str = None):
    obs = env.reset(difficulty)
    return obs.dict()


@app.post("/step")
def step(action: Action):
    obs, reward, done, _ = env.step(action)
    return {
        "observation": obs.dict(),
        "reward": reward,
        "done": done
    }


@app.get("/state")
def state():
    return env.state()


@app.get("/tasks")
def tasks():
    return {
        "tasks": [
            {"id": "easy", "description": "Simple projects"},
            {"id": "medium", "description": "Mixed quality projects"},
            {"id": "hard", "description": "Complex ambiguous projects"}
        ],
        "action_schema": {
            "score": "float (0-1)",
            "feedback": "string"
        }
    }
@app.get("/baseline")
def baseline():
    scores = []

    for _ in range(10):
        obs = env.reset()
        action = simple_policy(obs.dict())
        _, reward, _, _ = env.step(Action(**action))
        scores.append(reward)

    return {
        "baseline_score": sum(scores) / len(scores)
    }
@app.get("/grader")
def grader():
    return {
        "last_reward": env.last_reward
    }