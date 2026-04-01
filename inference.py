import asyncio
import os
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


def build_action(obs: dict, client: OpenAI) -> dict:
    score = 0.2

    if obs.get("has_tests"):
        score += 0.25
    if obs.get("has_docs"):
        score += 0.2
    if obs.get("has_docker"):
        score += 0.15
    if obs.get("stars", 0) > 100:
        score += 0.2

    feedback = []

    if not obs.get("has_tests", False):
        feedback.append("missing tests")
    if not obs.get("has_docs", False):
        feedback.append("missing documentation")
    if not obs.get("has_docker", False):
        feedback.append("no docker")

    model_feedback = get_model_message(client, obs)

    final_feedback = ", ".join(feedback) if feedback else model_feedback

    return {
        "score": max(0.0, min(1.0, score)),
        "feedback": final_feedback
    }


async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        reset_resp = requests.get(f"{SPACE_URL}/reset", timeout=30)
        reset_resp.raise_for_status()
        obs = reset_resp.json()

        done = False

        for step in range(1, MAX_STEPS + 1):
            if done:
                break

            action = build_action(obs, client)

            step_resp = requests.post(f"{SPACE_URL}/step", json=action, timeout=30)
            step_resp.raise_for_status()
            result = step_resp.json()

            reward = float(result.get("reward", 0.0))
            done = bool(result.get("done", False))
            obs = result.get("observation", obs)

            rewards.append(reward)
            steps_taken = step

            log_step(step=step, action=action, reward=reward, done=done, error=None)

            if done:
                break

        if rewards:
            score = sum(rewards) / len(rewards)
        score = max(0.0, min(1.0, score))
        success = score >= SUCCESS_SCORE_THRESHOLD

    except Exception as exc:
        print(f"[DEBUG] inference failed: {exc}", flush=True)

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    asyncio.run(main())