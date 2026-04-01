TASKS = {
    "easy": [
        {
            "features": ["todo"],
            "has_tests": False,
            "has_docs": True,
            "has_docker": False,
            "stars": 5,
            "difficulty": "easy",
            "true_score": 0.4,
            "issues": ["missing tests", "no docker"]
        },
        {
            "features": ["crud"],
            "has_tests": True,
            "has_docs": False,
            "has_docker": False,
            "stars": 15,
            "difficulty": "easy",
            "true_score": 0.6,
            "issues": ["missing documentation", "no docker"]
        }
    ],
    "medium": [
        {
            "features": ["auth", "crud"],
            "has_tests": False,
            "has_docs": False,
            "has_docker": True,
            "stars": 50,
            "difficulty": "medium",
            "true_score": 0.5,
            "issues": ["missing tests", "missing documentation"]
        },
        {
            "features": ["dashboard", "analytics"],
            "has_tests": True,
            "has_docs": False,
            "has_docker": False,
            "stars": 70,
            "difficulty": "medium",
            "true_score": 0.65,
            "issues": ["missing documentation", "no docker"]
        }
    ],
    "hard": [
        {
            "features": ["chat", "ai"],
            "has_tests": False,
            "has_docs": False,
            "has_docker": False,
            "stars": 200,
            "difficulty": "hard",
            "true_score": 0.3,
            "issues": ["missing tests", "missing documentation", "no docker"]
        },
        {
            "features": ["ml", "deployment", "monitoring"],
            "has_tests": True,
            "has_docs": False,
            "has_docker": True,
            "stars": 180,
            "difficulty": "hard",
            "true_score": 0.75,
            "issues": ["missing documentation"]
        }
    ]
}