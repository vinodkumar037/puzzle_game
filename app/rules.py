DIFFICULTY_ROLES = {
    "easy": {
        "operations": [0],
        "max_number": 10,
        "equations_per_levels": 1,
    },

    "medium": {
        "operations": [0,1],
        "max_number": 20,
        "equations_per_levels": 2,
    },

    "hard": {
        "operations": [0,1,2,3],
        "max_number": 50,
        "equations_per_levels": 3,
    }  
}

def get_difficulty_roles(difficulty: str):
    if difficulty not in DIFFICULTY_ROLES:
        raise ValueError(f"Invalid difficulty level: {difficulty}")

    return DIFFICULTY_ROLES[difficulty]