def reward_fn(pred_score, true_score, feedback, issues, difficulty="easy"):
    score_reward = 1 - abs(pred_score - true_score)

    feedback_reward = 0.0
    for issue in issues:
        if issue.lower() in feedback.lower():
            feedback_reward += 1.0

    if len(issues) > 0:
        feedback_reward /= len(issues)

    penalty = 0.0
    if "security" in feedback.lower() and "security" not in [i.lower() for i in issues]:
        penalty += 0.2

    total = (0.6 * score_reward) + (0.4 * feedback_reward) - penalty

    EPS = 1e-6
    return max(EPS, min(1.0 - EPS, total))