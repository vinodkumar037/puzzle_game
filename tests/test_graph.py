import sys
from pathlib import Path
from pprint import pprint

# Ensure project root directory is in sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.graph import puzzle_graph

if __name__ == "__main__":
    initial_state = {
        "rows": 3,
        "columns": 3,
        "difficulty": "easy"
    }

    result = puzzle_graph.invoke(initial_state)

    print("\n===== GRAPH RESULT =====")
    pprint(result)

    print("\n===== GENERATED LEVELS =====")
    pprint(result.get("levels", []))

    print("\n===== VALIDATION ERRORS =====")
    pprint(result.get("validation_errors", []))

    print("\n===== GENERATION ATTEMPTS =====")
    print(result.get("generation_attempts"))