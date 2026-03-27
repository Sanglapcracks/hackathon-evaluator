---
title: Hackathon Evaluator
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
app_file: main.py
pinned: false
---
# 🚀 Hackathon Project Evaluation Environment (OpenEnv)

## 📌 Overview

This project implements a real-world OpenEnv environment where an AI agent evaluates hackathon projects based on structured features such as documentation, testing, Docker support, and popularity.

The agent assigns a score (0–1) and provides feedback, and is rewarded based on accuracy and reasoning quality.

---

## 🎯 Motivation

Evaluating hackathon projects is time-consuming and subjective. This environment simulates a standardized evaluation system that can:

- Train AI evaluators
- Benchmark model reasoning
- Ensure fair and consistent scoring

---

## 🧠 Environment Design

### Observation Space

The agent receives:

- `features`: list of project features
- `has_tests`: boolean
- `has_docs`: boolean
- `has_docker`: boolean
- `stars`: integer (popularity)
- `difficulty`: easy / medium / hard

---

### Action Space

The agent must output:

- `score`: float (0–1)
- `feedback`: string explanation

---

### Reward Function

Reward is computed using:

- Score accuracy (distance from true score)
- Feedback correctness (mentions real issues)
- Penalty for hallucinations

Final reward is a value between **0 and 1**.

---

## 🧪 Tasks

The environment includes 3 difficulty levels:

### 🟢 Easy
- Basic projects
- Missing key components (tests, docs)

### 🟡 Medium
- Mixed quality projects
- Partial completeness

### 🔴 Hard
- Complex projects
- Subtle issues and ambiguity

---

## ⚙️ API Endpoints

- `/reset` → Start new task
- `/step` → Submit evaluation
- `/state` → View internal state
- `/tasks` → List tasks
- `/baseline` → Run baseline agent
- `/grader` → Get last reward

---

## 🤖 Baseline Agent

A simple heuristic-based agent evaluates projects based on:

- presence of tests
- documentation
- docker support
- popularity (stars)

### Baseline Score
~0.5–0.7 (varies slightly due to randomness)

---

## 🐳 Setup Instructions

### Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
=======
---
title: Hackathon Evaluator
emoji: 🦀
colorFrom: red
colorTo: green
sdk: docker
pinned: false
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
>>>>>>> 3b5e8bb97f294dbe97cffd36cbb1ae884a1f24b7
