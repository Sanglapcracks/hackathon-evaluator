import asyncio
import os
import json
from typing import List
import requests
from openai import OpenAI
from client import HackathonEnvClient

API_BASE_URL = os.environ["API_BASE_URL"]
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
API_KEY = os.environ["API_KEY"]

SPACE_URL = os.getenv(
    "SPACE_URL",
    "https://rockafellersang-hackathon-evaluator.hf.space"
)

MAX_STEPS = 4
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
POLICY_FILE = os.path.join(BASE_DIR, "policy.json")

POLICY = {
    "has_tests_weight": 0.25,
    "has_docs_weight": 0.20,
    "has_docker_weight": 0.15,
    "stars_weight": 0.20
}

if os.path.exists(POLICY_FILE):
    try:
        with open(POLICY_FILE, "r", encoding="utf-8") as f:
            POLICY.update(json.load(f))
    except Exception:
        pass

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
    prompt = (
        "You are evaluating a hackathon project.\n"
        f"Observation: {obs}\n"
        "Write a short judgment summary."
    )

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a careful hackathon judge."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=80,
        )
        text = (completion.choices[0].message.content or "").strip()
        return text if text else "basic evaluation"
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        return "basic evaluation"
def load_past_trajectories():
    if not os.path.exists(TRAJECTORY_FILE):
        return []

    records = []
    try:
        with open(TRAJECTORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        pass

    return records
def build_fingerprint(obs: dict) -> dict:
    return {
        "difficulty": obs.get("difficulty"),
        "visible_features": sorted(obs.get("visible_features", [])),
        "revealed_issues": sorted(obs.get("revealed_issues", [])),
        "revealed_signals_keywords": sorted([
            s.lower().split()[0] for s in obs.get("revealed_signals", []) if s
        ]),
    }


def observation_similarity(obs: dict, past_record: dict) -> float:
    """
    Better similarity using task fingerprints.
    """
    current_fp = build_fingerprint(obs)

    history = past_record.get("history", [])
    if not history:
        return 0.0

    first_obs = history[0].get("observation", {})
    past_fp = build_fingerprint(first_obs)

    score = 0.0

    # Difficulty match
    if current_fp["difficulty"] == past_fp["difficulty"]:
        score += 2.0

    # Feature overlap
    current_features = set(current_fp["visible_features"])
    past_features = set(past_fp["visible_features"])
    score += len(current_features & past_features) * 1.5

    # Revealed issue overlap
    current_issues = set(current_fp["revealed_issues"])
    past_issues = set(past_fp["revealed_issues"])
    score += len(current_issues & past_issues) * 2.0

    # Signal keyword overlap
    current_signal_keys = set(current_fp["revealed_signals_keywords"])
    past_signal_keys = set(past_fp["revealed_signals_keywords"])
    score += len(current_signal_keys & past_signal_keys) * 1.0

    return score


def retrieve_best_past_case(obs: dict):
    past_records = load_past_trajectories()
    if not past_records:
        return None

    successful = [
        r for r in past_records
        if r.get("success") is True or r.get("score", 0.0) > 0.7
    ]

    if not successful:
        return None

    ranked = []
    for record in successful:
        sim = observation_similarity(obs, record)
        quality = record.get("score", 0.0)
        combined = sim + quality
        ranked.append((combined, record))

    ranked.sort(key=lambda x: x[0], reverse=True)

    return ranked[0][1] if ranked else None


def choose_inspection(obs: dict, history: List[dict]) -> str:
    used_actions = {h["action"]["action_type"] for h in history if "action" in h}

    inspection_order = [
        "inspect_tests",
        "inspect_docs",
        "inspect_docker",
        "inspect_popularity",
    ]

    for action_type in inspection_order:
        if action_type not in used_actions:
            return action_type

    return "inspect_popularity"


def build_final_submission(obs: dict, client: OpenAI, last_reward: float, history: List[dict]) -> dict:
    revealed_issues = obs.get("revealed_issues", [])
    revealed_signals = obs.get("revealed_signals", [])

    # Retrieve similar past successful case
    past_case = retrieve_best_past_case(obs)
    past_final_action = None

    if past_case and past_case.get("history"):
        for item in reversed(past_case["history"]):
            action = item.get("action", {})
            if action.get("action_type") == "submit_final":
                past_final_action = action
                break

    score = 0.15

    if "missing tests" not in revealed_issues:
        score += POLICY["has_tests_weight"]
    if "missing documentation" not in revealed_issues:
        score += POLICY["has_docs_weight"]
    if "no docker" not in revealed_issues:
        score += POLICY["has_docker_weight"]

    if any(
        "200 stars" in s or "180 stars" in s or "50 stars" in s or "70 stars" in s or "15 stars" in s or "5 stars" in s
        for s in revealed_signals
    ):
        score += POLICY["stars_weight"]

    if last_reward > 0.7:
        score += 0.03
    elif last_reward < 0.4:
        score -= 0.05

    score += MEMORY["best_score_bias"]

    # Blend with retrieved successful past score
    if past_final_action and past_final_action.get("score") is not None:
        score = 0.7 * score + 0.3 * float(past_final_action["score"])

    score = max(0.0, min(1.0, score))

    feedback_parts = list(revealed_issues)

    if MEMORY["best_feedback_phrases"]:
        for phrase in MEMORY["best_feedback_phrases"]:
            if phrase not in feedback_parts and len(feedback_parts) < 4:
                feedback_parts.append(phrase)

    # Reuse phrases from similar successful past final action
    if past_final_action and past_final_action.get("feedback"):
        for phrase in str(past_final_action["feedback"]).split(","):
            phrase = phrase.strip()
            if phrase and phrase not in feedback_parts and len(feedback_parts) < 5:
                feedback_parts.append(phrase)

    model_summary = get_model_message(client, obs)

    if model_summary and model_summary not in feedback_parts and len(feedback_parts) < 6:
        feedback_parts.append(model_summary)

    feedback = ", ".join(feedback_parts) if feedback_parts else model_summary

    previous_feedbacks = {h["action"].get("feedback", "") for h in history if "action" in h}
    if feedback in previous_feedbacks:
        feedback += ", needs further review"

    if past_case:
        print(f"[DEBUG] Retrieved past case with score={past_case.get('score')}", flush=True)

    return {
        "action_type": "submit_final",
        "score": score,
        "feedback": feedback
    }

def build_action(obs: dict, client: OpenAI, last_reward: float = 0.0, history: List[dict] = None) -> dict:
    if history is None:
        history = []

    current_step = obs.get("current_step", 0)
    remaining_budget = obs.get("remaining_budget", 0)
    can_submit = obs.get("can_submit", False)
    revealed_signals = obs.get("revealed_signals", [])
    past_case = retrieve_best_past_case(obs)
    past_final_action = None

    if past_case and past_case.get("history"):
        for item in reversed(past_case["history"]):
            action = item.get("action", {})
            if action.get("action_type") == "submit_final":
                past_final_action = action
                break

    # Submit if enough evidence is gathered or budget is low
    if can_submit and (len(revealed_signals) >= 2 or remaining_budget <= 1 or current_step >= 2):
        return build_final_submission(obs, client, last_reward, history)

    return {
        "action_type": choose_inspection(obs, history)
    }


async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env_client=HackathonEnvClient(SPACE_URL)

    rewards: List[float] = []
    history: List[dict] = []
    steps_taken = 0
    score = 0.0
    success = False
    last_reward = 0.0

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        obs = env_client.reset()

        done = False

        for step in range(1, MAX_STEPS + 1):
            if done:
                break

            action = build_action(obs, client, last_reward=last_reward, history=history)

            result = env_client.step(action)

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
        learning_rate = 0.05

        if score > 0.7:
            POLICY["has_tests_weight"] = min(0.4, POLICY["has_tests_weight"] + learning_rate * 0.5)
            POLICY["has_docs_weight"] = min(0.35, POLICY["has_docs_weight"] + learning_rate * 0.4)
            POLICY["has_docker_weight"] = min(0.3, POLICY["has_docker_weight"] + learning_rate * 0.3)
            POLICY["stars_weight"] = min(0.3, POLICY["stars_weight"] + learning_rate * 0.2)
        else:
            POLICY["has_tests_weight"] = max(0.05, POLICY["has_tests_weight"] - learning_rate * 0.2)
            POLICY["has_docs_weight"] = max(0.05, POLICY["has_docs_weight"] - learning_rate * 0.2)
            POLICY["has_docker_weight"] = max(0.05, POLICY["has_docker_weight"] - learning_rate * 0.15)
            POLICY["stars_weight"] = max(0.05, POLICY["stars_weight"] - learning_rate * 0.1)

        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(MEMORY, f, indent=2)
            print(f"[DEBUG] MEMORY SAVED → {MEMORY_FILE}", flush=True)
        except Exception as e:
            print(f"[DEBUG] Failed to save memory: {e}", flush=True)
        try:
            with open(POLICY_FILE, "w", encoding="utf-8") as f:
                json.dump(POLICY, f, indent=2)
            print(f"[DEBUG] POLICY SAVED → {POLICY_FILE}", flush=True)
        except Exception as e:
            print(f"[DEBUG] Failed to save policy: {e}", flush=True)

        try:
            with open(TRAJECTORY_FILE, "a", encoding="utf-8") as f:
                record = {
                    "task": TASK_NAME,
                    "model": MODEL_NAME,
                    "success": success,
                    "score": score,
                    "rewards": rewards,
                    "history": history,
                    "fingerprint":build_fingerprint(obs)
                }
                f.write(json.dumps(record) + "\n")
            print(f"[DEBUG] TRAJECTORY SAVED → {TRAJECTORY_FILE}", flush=True)
        except Exception as e:
            print(f"[DEBUG] Failed to save trajectory: {e}", flush=True)

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