from fastapi import FastAPI
from app.env import HackathonEnv
from app.models import Action

app = FastAPI(
    title="Hackathon Evaluator",
    docs_url="/docs",
    openapi_url="/openapi.json",
    root_path="/"
)

env = HackathonEnv()
def simple_policy(obs):
    score = 0.2

    # ------------------------
    # Heuristic scoring
    # ------------------------
    if obs["has_tests"]:
        score += 0.25

    if obs["has_docs"]:
        score += 0.2

    if obs["has_docker"]:
        score += 0.15

    if obs["stars"] > 100:
        score += 0.2

    # ------------------------
    # Feedback generation
    # ------------------------
    feedback = []

    if not obs["has_tests"]:
        feedback.append("no tests")

    if not obs["has_docs"]:
        feedback.append("no documentation")

    if not obs["has_docker"]:
        feedback.append("no docker")

    if len(feedback) == 0:
        feedback.append("well structured project")

    return {
        "score": min(score, 1),
        "feedback": ", ".join(feedback)
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
    runs = []

    for _ in range(10):
        obs = env.reset()
        action_dict = simple_policy(obs.dict())

        obs2, reward, done, _ = env.step(Action(**action_dict))

        scores.append(reward)

        runs.append({
            "observation": obs.dict(),
            "action": action_dict,
            "reward": reward
        })

    return {
        "baseline_score": sum(scores) / len(scores),
        "runs": runs
    }
@app.get("/grader")
def grader():
    return {
        "last_reward": env.last_reward
    }