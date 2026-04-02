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
    """
    Baseline policy for the new multi-step evidence-gathering environment.
    """
    # If we have not inspected enough, gather more evidence first
    if "No automated tests were found." not in obs.get("revealed_signals", []) and obs.get("remaining_budget", 0) > 2:
        return {"action_type": "inspect_tests"}

    if "README does not describe model behavior or evaluation." not in obs.get("revealed_signals", []) and obs.get("remaining_budget", 0) > 1:
        return {"action_type": "inspect_docs"}

    # If we have at least some evidence, submit final
    feedback = ", ".join(obs.get("revealed_issues", [])) if obs.get("revealed_issues") else "basic evaluation"

    score = 0.7
    if "missing tests" in obs.get("revealed_issues", []):
        score -= 0.2
    if "missing documentation" in obs.get("revealed_issues", []):
        score -= 0.15
    if "no docker" in obs.get("revealed_issues", []):
        score -= 0.15

    score = max(0.0, min(1.0, score))

    return {
        "action_type": "submit_final",
        "score": score,
        "feedback": feedback
    }


@app.get("/")
def home():
    return {"message": "Hackathon Evaluator Environment Running"}


@app.get("/reset")
def reset(difficulty: str = None):
    obs = env.reset(difficulty)
    return obs.model_dump() if hasattr(obs, "model_dump") else obs.dict()


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
    return {
        "state": env.state(),
        "current_step": env.current_step,
        "max_steps": env.max_steps,
        "done": env.done,
        "last_reward": env.last_reward
    }


@app.get("/tasks")
def tasks():
    return {
        "tasks": [
            {
                "id": "easy",
                "description": "Simple projects with obvious engineering issues. Agent should inspect evidence before final submission."
            },
            {
                "id": "medium",
                "description": "Projects with mixed quality and incomplete evidence. Agent must gather evidence selectively."
            },
            {
                "id": "hard",
                "description": "Complex or deceptive projects where popularity may hide engineering gaps. Agent must reason over partial evidence."
            }
        ],
        "workflow": [
            "reset environment",
            "inspect one or more aspects of the project",
            "observe revealed signals and issues",
            "submit final score and feedback"
        ],
        "action_schema": {
            "action_type": "inspect_tests | inspect_docs | inspect_docker | inspect_popularity | submit_final",
            "score": "float (required only for submit_final)",
            "feedback": "string (required only for submit_final)"
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

        while not done:
            obs_dict = obs.model_dump() if hasattr(obs, "model_dump") else obs.dict()
            action_dict = simple_policy(obs_dict)

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