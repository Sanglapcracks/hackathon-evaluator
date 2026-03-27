def reward_fn(pred_score, true_score, feedback, issues):
    """
    pred_score: agent's predicted score
    true_score: actual correct score
    feedback: agent's explanation
    issues: actual problems in project
    """

    # 1. Score accuracy (main signal)
    score_reward = 1 - abs(pred_score - true_score)

    # 2. Feedback correctness
    feedback_reward = 0
    for issue in issues:
        if issue.lower() in feedback.lower():
            feedback_reward += 1

    if len(issues) > 0:
        feedback_reward /= len(issues)

    # 3. Hallucination penalty (agent mentions wrong issues)
    penalty = 0
    if "security" in feedback.lower() and "security" not in issues:
        penalty += 0.2

    # 4. Final reward
    total = (0.6 * score_reward) + (0.4 * feedback_reward) - penalty

    # Clamp between 0 and 1
    return max(0, min(1, total))