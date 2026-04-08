from fastapi import FastAPI
from server.env import HackathonEnv
from server.models import Action
from fastapi import Body
from typing import Optional, Dict
from server.tasks import get_all_tasks
from server.tasks import get_task_by_id
from server.grader import reward_fn

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





@app.post("/reset")
def reset_post(payload: Optional[Dict] = Body(default={})):
    difficulty = payload.get("difficulty") if payload else None
    obs = env.reset(difficulty)
    return obs.model_dump() if hasattr(obs, "model_dump") else obs.dict()


# Keep GET for manual testing
@app.get("/reset")
def reset_get(difficulty: str = None):
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
    task_list = []
    for task in get_all_tasks():
        task_list.append({
            "id": task["id"],
            "difficulty": task["difficulty"],
            "description": f"Evaluate project with features: {', '.join(task['visible_features'])}",
            "grader": "reward_fn"
        })

    return {
        "tasks": task_list,
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


@app.post("/grader")
def grader(payload: Optional[Dict] = Body(default={})):
    task_id = payload.get("task_id")
    score = payload.get("score", 0.0)
    feedback = payload.get("feedback", "")

    task = get_task_by_id(task_id)
    if task is None:
        return {
            "error": f"Unknown task_id: {task_id}"
        }

    grader_score = reward_fn(
        pred_score=score,
        true_score=task.get("true_score", 0.0),
        feedback=feedback,
        issues=task.get("issues", []),
        difficulty=task.get("difficulty", "easy")
    )

    return {
        "task_id": task_id,
        "grader_score": grader_score,
        "difficulty": task.get("difficulty"),
        "true_score": task.get("true_score"),
        "issues": task.get("issues", [])
    }


def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()