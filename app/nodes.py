import os
from app.generator import generate_level

def generate_node(state):
    number_of_levels = int(os.getenv("NUMBER_OF_LEVELS", "10"))

    levels = []

    for level_number in range(1, number_of_levels + 1):
        level = generate_level(
            rows=state["rows"],
            columns=state["columns"],
            difficulty=state["difficulty"],
            level_number=level_number
        )
        levels.append(level)

    return {
        "levels": levels
    }

