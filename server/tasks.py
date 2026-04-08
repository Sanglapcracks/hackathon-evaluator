TASKS = {
    "easy": [
        {
            "id": "easy_todo",
            "visible_features": ["todo app"],
            "revealed_issues": [],
            "revealed_signals": [],
            "hidden_evidence": {
                "inspect_tests": {"signal": "No tests found.", "issue": "missing tests"},
                "inspect_docs": {"signal": "Basic README exists.", "issue": None},
                "inspect_docker": {"signal": "No Dockerfile.", "issue": "no docker"},
                "inspect_popularity": {"signal": "5 stars.", "issue": None}
            },
            "difficulty": "easy",
            "true_score": 0.4,
            "issues": ["missing tests", "no docker"]
        },
        {
            "id": "easy_blog_app",
            "visible_features": ["blog", "web"],
            "revealed_issues": [],
            "revealed_signals": [],
            "hidden_evidence": {
                "inspect_tests": {"signal": "Basic tests exist.", "issue": None},
                "inspect_docs": {"signal": "README missing usage section.", "issue": "missing documentation"},
                "inspect_docker": {"signal": "No containerization.", "issue": "no docker"},
                "inspect_popularity": {"signal": "12 stars.", "issue": None}
            },
            "difficulty": "easy",
            "true_score": 0.5,
            "issues": ["missing documentation", "no docker"]
        }
    ],

    "medium": [
        {
            "id": "medium_auth_crud",
            "visible_features": ["auth", "crud"],
            "revealed_issues": [],
            "revealed_signals": [],
            "hidden_evidence": {
                "inspect_tests": {"signal": "No auth tests.", "issue": "missing tests"},
                "inspect_docs": {"signal": "Docs incomplete.", "issue": "missing documentation"},
                "inspect_docker": {"signal": "Dockerfile present.", "issue": None},
                "inspect_popularity": {"signal": "50 stars.", "issue": None}
            },
            "difficulty": "medium",
            "true_score": 0.5,
            "issues": ["missing tests", "missing documentation"]
        },
        {
            "id": "medium_api_service",
            "visible_features": ["api", "service"],
            "revealed_issues": [],
            "revealed_signals": [],
            "hidden_evidence": {
                "inspect_tests": {"signal": "Tests exist.", "issue": None},
                "inspect_docs": {"signal": "README lacks API docs.", "issue": "missing documentation"},
                "inspect_docker": {"signal": "Dockerfile present.", "issue": None},
                "inspect_popularity": {"signal": "80 stars.", "issue": None}
            },
            "difficulty": "medium",
            "true_score": 0.6,
            "issues": ["missing documentation"]
        }
    ],

    "hard": [
        {
            "id": "hard_chat_ai",
            "visible_features": ["chat", "ai"],
            "revealed_issues": [],
            "revealed_signals": [],
            "hidden_evidence": {
                "inspect_tests": {"signal": "No tests.", "issue": "missing tests"},
                "inspect_docs": {"signal": "Docs missing.", "issue": "missing documentation"},
                "inspect_docker": {"signal": "No Docker.", "issue": "no docker"},
                "inspect_popularity": {"signal": "200 stars.", "issue": None}
            },
            "difficulty": "hard",
            "true_score": 0.3,
            "issues": ["missing tests", "missing documentation", "no docker"]
        },
        {
            "id": "hard_ml_pipeline",
            "visible_features": ["ml", "pipeline"],
            "revealed_issues": [],
            "revealed_signals": [],
            "hidden_evidence": {
                "inspect_tests": {"signal": "Partial tests.", "issue": None},
                "inspect_docs": {"signal": "No model explanation.", "issue": "missing documentation"},
                "inspect_docker": {"signal": "Dockerfile exists.", "issue": None},
                "inspect_popularity": {"signal": "150 stars.", "issue": None}
            },
            "difficulty": "hard",
            "true_score": 0.65,
            "issues": ["missing documentation"]
        }
    ]
}
def get_all_tasks():
    all_tasks = []
    for group in TASKS.values():
        all_tasks.extend(group)
    return all_tasks


def get_task_by_id(task_id: str):
    for task in get_all_tasks():
        if task.get("id") == task_id:
            return task
    return None