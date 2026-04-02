from fastapi import FastAPI
from server.env import HackathonEnv
from server.models import Action

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
    obs, reward, done, info = env.step(action)
    obs_dict = obs.model_dump() if hasattr(obs, "model_dump") else obs.dict()

    return {
        "observation": obs_dict,
        "reward": reward,
        "done": done,
        "info": info
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

    for _ in range(5):
        obs = env.reset()
        done = False
        episode_rewards = []
        trajectory = []
        last_reward = 0.0

        while not done:
            obs_dict = obs.model_dump() if hasattr(obs, "model_dump") else obs.dict()
            action_dict = simple_policy(obs_dict)

            if last_reward < 0.4:
                action_dict["score"] = max(0.0, action_dict["score"] - 0.1)
            elif last_reward > 0.7:
                action_dict["score"] = min(1.0, action_dict["score"] + 0.05)

            next_obs, reward, done, info = env.step(Action(**action_dict))
            next_obs_dict = next_obs.model_dump() if hasattr(next_obs, "model_dump") else next_obs.dict()

            trajectory.append({
                "observation": obs_dict,
                "action": action_dict,
                "reward": reward,
                "done": done,
                "info": info
            })

            episode_rewards.append(reward)
            last_reward = reward
            obs = next_obs

        episode_score = sum(episode_rewards) / len(episode_rewards)
        scores.append(episode_score)

        runs.append({
            "episode_score": episode_score,
            "episode_rewards": episode_rewards,
            "trajectory": trajectory
        })

    return {
        "baseline_score": sum(scores) / len(scores),
        "runs": runs
    }
@app.get("/grader")
def grader():
    return {
        "last_reward": env.last_reward,
        "done": env.done,
        "current_step": env.current_step,
        "max_steps": env.max_steps
    }
def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()