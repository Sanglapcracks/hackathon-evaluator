def reward_fn(pred_score, true_score, feedback, issues, difficulty="medium"):
    # ------------------------
    # 1. Score accuracy
    # ------------------------
    score_reward = 1 - abs(pred_score - true_score)

    # ------------------------
    # 2. Feedback matching (flexible)
    # ------------------------
    feedback_lower = feedback.lower()
    feedback_reward = 0

    for issue in issues:
        words = issue.lower().split()
        for word in words:
            if word in feedback_lower:
                feedback_reward += 0.2
                break

    if len(issues) > 0:
        feedback_reward = min(feedback_reward, 1)

    # ------------------------
    # 3. Hallucination penalty (generalized)
    # ------------------------
    penalty = 0

    common_fake_issues = ["security", "performance", "scalability"]

    for fake in common_fake_issues:
        if fake in feedback_lower and fake not in " ".join(issues).lower():
            penalty += 0.1

    # ------------------------
    # 4. Difficulty scaling
    # ------------------------
    difficulty_bonus = {
        "easy": 1.0,
        "medium": 1.1,
        "hard": 1.2
    }

    base_reward = (0.6 * score_reward) + (0.4 * feedback_reward) - penalty

    reward = base_reward * difficulty_bonus.get(difficulty, 1.0)

    # ------------------------
    # Clamp
    # ------------------------
    return max(0, min(1, reward))