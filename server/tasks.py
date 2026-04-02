TASKS = {
    "easy": [
        {
            "visible_features": ["todo app"],
            "revealed_issues": [],
            "revealed_signals": [],
            "hidden_evidence": {
                "inspect_tests": {
                    "signal": "No automated tests were found.",
                    "issue": "missing tests"
                },
                "inspect_docs": {
                    "signal": "README has setup instructions but no usage examples.",
                    "issue": None
                },
                "inspect_docker": {
                    "signal": "No Dockerfile found.",
                    "issue": "no docker"
                },
                "inspect_popularity": {
                    "signal": "Repository has 5 stars.",
                    "issue": None
                }
            },
            "difficulty": "easy",
            "true_score": 0.4,
            "issues": ["missing tests", "no docker"]
        },
        {
            "visible_features": ["crud app"],
            "revealed_issues": [],
            "revealed_signals": [],
            "hidden_evidence": {
                "inspect_tests": {
                    "signal": "Basic test suite exists for core endpoints.",
                    "issue": None
                },
                "inspect_docs": {
                    "signal": "README is missing detailed documentation.",
                    "issue": "missing documentation"
                },
                "inspect_docker": {
                    "signal": "No Dockerfile found.",
                    "issue": "no docker"
                },
                "inspect_popularity": {
                    "signal": "Repository has 15 stars.",
                    "issue": None
                }
            },
            "difficulty": "easy",
            "true_score": 0.6,
            "issues": ["missing documentation", "no docker"]
        }
    ],
    "medium": [
        {
            "visible_features": ["auth", "crud"],
            "revealed_issues": [],
            "revealed_signals": [],
            "hidden_evidence": {
                "inspect_tests": {
                    "signal": "No tests for authentication flows were found.",
                    "issue": "missing tests"
                },
                "inspect_docs": {
                    "signal": "README does not explain configuration or architecture.",
                    "issue": "missing documentation"
                },
                "inspect_docker": {
                    "signal": "Dockerfile exists and builds correctly.",
                    "issue": None
                },
                "inspect_popularity": {
                    "signal": "Repository has 50 stars.",
                    "issue": None
                }
            },
            "difficulty": "medium",
            "true_score": 0.5,
            "issues": ["missing tests", "missing documentation"]
        },
        {
            "visible_features": ["dashboard", "analytics"],
            "revealed_issues": [],
            "revealed_signals": [],
            "hidden_evidence": {
                "inspect_tests": {
                    "signal": "Test coverage exists for major analytics modules.",
                    "issue": None
                },
                "inspect_docs": {
                    "signal": "README lacks deployment and configuration guidance.",
                    "issue": "missing documentation"
                },
                "inspect_docker": {
                    "signal": "No Dockerfile found.",
                    "issue": "no docker"
                },
                "inspect_popularity": {
                    "signal": "Repository has 70 stars.",
                    "issue": None
                }
            },
            "difficulty": "medium",
            "true_score": 0.65,
            "issues": ["missing documentation", "no docker"]
        }
    ],
    "hard": [
        {
            "visible_features": ["chat", "ai"],
            "revealed_issues": [],
            "revealed_signals": [],
            "hidden_evidence": {
                "inspect_tests": {
                    "signal": "No automated regression tests were found.",
                    "issue": "missing tests"
                },
                "inspect_docs": {
                    "signal": "README does not describe model behavior or evaluation.",
                    "issue": "missing documentation"
                },
                "inspect_docker": {
                    "signal": "No containerization setup found.",
                    "issue": "no docker"
                },
                "inspect_popularity": {
                    "signal": "Repository has 200 stars despite missing engineering basics.",
                    "issue": None
                }
            },
            "difficulty": "hard",
            "true_score": 0.3,
            "issues": ["missing tests", "missing documentation", "no docker"]
        },
        {
            "visible_features": ["ml", "deployment", "monitoring"],
            "revealed_issues": [],
            "revealed_signals": [],
            "hidden_evidence": {
                "inspect_tests": {
                    "signal": "Tests exist for deployment scripts and monitoring checks.",
                    "issue": None
                },
                "inspect_docs": {
                    "signal": "Documentation is incomplete for onboarding and architecture.",
                    "issue": "missing documentation"
                },
                "inspect_docker": {
                    "signal": "Dockerfile and compose setup are present.",
                    "issue": None
                },
                "inspect_popularity": {
                    "signal": "Repository has 180 stars.",
                    "issue": None
                }
            },
            "difficulty": "hard",
            "true_score": 0.75,
            "issues": ["missing documentation"]
        }
    ]
}