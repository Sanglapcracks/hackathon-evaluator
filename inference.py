import asyncio
import os
import json
from typing import List
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
API_KEY = os.getenv("HF-TOKEN", "dummy-key")

SPACE_URL = os.getenv(
    "SPACE_URL",
    "https://rockafellersang-hackathon-evaluator.hf.space"
)

MAX_STEPS = 3
SUCCESS_SCORE_THRESHOLD = 0.5
TASK_NAME = "hackathon_eval"
BENCHMARK = "hackathon_evaluator"
MEMORY = {
    "best_score_bias": 0.0,
    "best_feedback_phrases": [],
    "episode_count": 0
}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(BASE_DIR, "memory.json")
TRAJECTORY_FILE = os.path.join(BASE_DIR, "trajectories.jsonl")
SFT_FILE = os.path.join(BASE_DIR, "sft_data.jsonl")
if os.path.exists(MEMORY_FILE):
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            MEMORY.update(json.load(f))
    except Exception:
        pass

def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step, action, reward, done, error):
    print(
        f"[STEP] step={step} action={action} reward={reward} done={done} error={error}",
        flush=True
    )


def log_end(success, steps, score, rewards):
    print(
        f"[END] success={success} steps={steps} score={score} rewards={rewards}",
        flush=True
    )


def get_model_message(client: OpenAI, obs: dict) -> str:
    """
    Uses OpenAI client as required.
    Falls back safely if request fails.
    """
    prompt = (
        "You are evaluating a hackathon project.\n"
        f"Project observation: {obs}\n"
        "Return a short feedback string about the project quality."
    )

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a hackathon judge."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=60,
        )
        text = (completion.choices[0].message.content or "").strip()
        return text if text else "basic evaluation"
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        return "basic evaluation"

def build_action(obs: dict, client: OpenAI, last_reward: float = 0.0, history: List[dict] = None) -> dict:
    if history is None:
        history = []

    score = 0.2

    if obs.get("has_tests"):
        score += 0.25
    if obs.get("has_docs"):
        score += 0.2
    if obs.get("has_docker"):
        score += 0.15
    if obs.get("stars", 0) > 100:
        score += 0.2

    # Step-aware adaptation
    current_step = obs.get("current_step", 0)
    max_steps = obs.get("max_steps", 3)

    # If previous reward was weak, adjust more aggressively
    if last_reward < 0.4:
        score -= 0.15
    elif last_reward < 0.7:
        score -= 0.05
    else:
        score += 0.05
    score+=MEMORY["best_score_bias"]

    # Later steps should refine rather than repeat blindly
    if current_step == max_steps - 1:
        score = min(score + 0.05, 1.0)

    score = max(0.0, min(1.0, score))

    feedback = []

    if not obs.get("has_tests", False):
        feedback.append("missing tests")
    if not obs.get("has_docs", False):
        feedback.append("missing documentation")
    if not obs.get("has_docker", False):
        feedback.append("no docker")
    if MEMORY["best_feedback_phrases"]:
        for phrase in MEMORY["best_feedback_phrases"]:
            if phrase not in feedback and len(feedback) < 4:
                feedback.append(phrase)


    # Use history to avoid repeating the exact same phrasing every step
    previous_feedbacks = {h["action"]["feedback"] for h in history if "action" in h}

    if current_step == 1 and "missing tests" not in ", ".join(feedback):
        feedback.append("engineering quality needs improvement")

    if current_step == 2 and obs.get("stars", 0) > 100:
        feedback.append("high popularity does not fully offset missing engineering fundamentals")

    candidate_feedback = ", ".join(feedback) if feedback else get_model_message(client, obs)

    if candidate_feedback in previous_feedbacks:
        candidate_feedback += ", needs further review"

    return {
        "score": score,
        "feedback": candidate_feedback
    }

async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    rewards: List[float] = []
    history: List[dict] = []
    steps_taken = 0
    score = 0.0
    success = False
    last_reward = 0.0

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        reset_resp = requests.get(f"{SPACE_URL}/reset", timeout=30)
        reset_resp.raise_for_status()
        obs = reset_resp.json()

        done = False

        for step in range(1, MAX_STEPS + 1):
            if done:
                break

            action = build_action(obs, client, last_reward=last_reward, history=history)

            step_resp = requests.post(f"{SPACE_URL}/step", json=action, timeout=30)
            step_resp.raise_for_status()
            result = step_resp.json()

            reward = float(result.get("reward", 0.0))
            done = bool(result.get("done", False))
            obs = result.get("observation", obs)

            rewards.append(reward)
            steps_taken = step
            last_reward = reward

            history.append({
                "step": step,
                "action": action,
                "reward": reward
            })

            log_step(step=step, action=action, reward=reward, done=done, error=None)

            if done:
                break

        if rewards:
            score = sum(rewards) / len(rewards)
        score = max(0.0, min(1.0, score))
        success = score >= SUCCESS_SCORE_THRESHOLD
        MEMORY["episode_count"] += 1

        if score > 0.7:
            MEMORY["best_score_bias"] = min(MEMORY["best_score_bias"] + 0.02, 0.15)

            for item in history:
                action_feedback = item.get("action", {}).get("feedback", "")
                for phrase in action_feedback.split(","):
                    phrase = phrase.strip()
                    if phrase and phrase not in MEMORY["best_feedback_phrases"]:
                        MEMORY["best_feedback_phrases"].append(phrase)
        else:
            MEMORY["best_score_bias"] = max(MEMORY["best_score_bias"] - 0.01, -0.15)
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(MEMORY, f, indent=2)
            print(f"[DEBUG] MEMORY SAVED → {MEMORY_FILE}", flush=True)
        except Exception as e:
            print(f"[DEBUG] Failed to save memory: {e}", flush=True)
        # SAVE TRAJECTORY (SFT DATA)
        try:
            with open(TRAJECTORY_FILE, "a", encoding="utf-8") as f:
                record = {
                    "task": TASK_NAME,
                    "model": MODEL_NAME,
                    "success": success,
                    "score": score,
                    "rewards": rewards,
                    "history": history
                }
                f.write(json.dumps(record) + "\n")

            print(f"[DEBUG] TRAJECTORY SAVED → {TRAJECTORY_FILE}", flush=True)

        except Exception as e:
            print(f"[DEBUG] Failed to save trajectory: {e}", flush=True)
                # SAVE ONLY GOOD TRAJECTORIES FOR SFT
        if success or score > 0.7:
            try:
                with open(SFT_FILE, "a", encoding="utf-8") as f:
                    sft_record = {
                        "input": {
                            "task": TASK_NAME,
                            "history": history[:-1] if len(history) > 1 else [],
                            "final_observation": obs
                        },
                        "output": history[-1]["action"] if history else {},
                        "score": score
                    }
                    f.write(json.dumps(sft_record) + "\n")

                print(f"[DEBUG] SFT SAMPLE SAVED → {SFT_FILE}", flush=True)

            except Exception as e:
                print(f"[DEBUG] Failed to save SFT sample: {e}", flush=True)

    except Exception as exc:
        print(f"[DEBUG] inference failed: {exc}", flush=True)

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    asyncio.run(main())