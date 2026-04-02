---
title: Hackathon Evaluator Environment
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
app_file: main.py
pinned: false
---


## Multi-Step Adaptive Agent

The environment now supports multi-step trajectories. The inference agent adapts within an episode using reward feedback and across episodes using persistent memory stored in `memory.json`. Successful trajectories are also saved in `sft_data.jsonl` for future supervised fine-tuning.
# Hackathon Evaluator (OpenEnv Environment)

An OpenEnv-compatible environment for evaluating hackathon projects using multi-step reasoning, adaptive agents, and trajectory-based learning.

---

## 🚀 Overview

This project simulates a hackathon judge that:

- inspects different aspects of a project
- gathers evidence across multiple steps
- produces a final score and feedback
- learns from past trajectories and adapts over time

---

## 🧠 Key Features

### 1. Multi-step environment
Agents must:
- inspect tests, docs, docker, popularity
- gather evidence
- submit a final evaluation

### 2. Progressive observations
The agent does NOT see everything initially:
- evidence is revealed through actions
- encourages reasoning over time

### 3. Reward-based learning
- rewards depend on correctness + evidence usage
- early submission is penalized

### 4. Persistent memory
- `memory.json` stores learned behavior
- improves across runs

### 5. Trajectory logging
- `trajectories.jsonl` stores all episodes
- `sft_data.jsonl` stores high-quality samples

### 6. Retrieval-based adaptation
- agent retrieves similar past successful cases
- reuses strategies dynamically

### 7. Learned policy weights
- `policy.json` updates feature importance over time
- reward-driven adaptation

---

## ⚙️ Environment API

### Reset
### Step
Example actions:
```json
{"action_type":"inspect_tests"}
{
  "action_type": "submit_final",
  "score": 0.4,
  "feedback": "missing tests, no docker"
}