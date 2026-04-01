---
title: Hackathon Evaluator Environment
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
app_file: main.py
pinned: false
---

# 🚀 Hackathon Project Evaluator (OpenEnv)

## 📌 Overview

This environment simulates a **real-world hackathon judging system** where an AI agent evaluates project submissions.

The agent must:
- Assign a score (0–1)
- Provide feedback explaining issues

This mirrors real judging tasks in hackathons, code reviews, and technical evaluations.

---

## 🧠 Motivation

Evaluating hackathon projects is:
- subjective
- multi-factor
- reasoning-heavy

This environment tests:
- scoring accuracy
- reasoning ability via feedback
- consistency across difficulty levels

---

## 🧱 Environment Design

### Observation Space

```json
{
  "features": ["list of features"],
  "has_tests": "bool",
  "has_docs": "bool",
  "has_docker": "bool",
  "stars": "int",
  "difficulty": "easy | medium | hard"
}