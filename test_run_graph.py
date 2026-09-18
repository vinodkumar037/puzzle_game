import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load app/.env if present
env_path = Path(__file__).parent / "app" / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

from app.graph import puzzle_graph

def main():
    print("==========================================")
    print("   Testing Puzzle LangGraph Workflow")
    print("==========================================")
    
    target_levels = os.getenv("NUMBER_OF_LEVELS", "5")
    max_attempts = os.getenv("MAX_ATTEMPTS", "5")
    
    print(f"Configured NUMBER_OF_LEVELS : {target_levels}")
    print(f"Configured MAX_ATTEMPTS      : {max_attempts}\n")

    initial_state = {
        "rows": 5,
        "columns": 5,
        "difficulty": "medium"
    }

    print(f"Invoking puzzle_graph with initial state:\n{initial_state}\n")
    print("Running graph nodes (generate -> validate -> should_continue -> save)...")
    print("--------------------------------------------------")

    result = puzzle_graph.invoke(initial_state)

    print("--------------------------------------------------")
    print("\nExecution Completed!")
    print(f"Generation Attempts Executed : {result.get('generation_attempts')}")
    
    valid_levels = result.get("levels", [])
    print(f"Valid Levels Returned        : {len(valid_levels)}")
    
    errors = result.get("validation_errors", [])
    if errors:
        print(f"\nValidation & Duplicate Log ({len(errors)} events):")
        for err in errors:
            print(f"  - {err}")

    for idx, level in enumerate(valid_levels, 1):
        print(f"\n--- Verified Level #{idx} ---")
        print(f"Grid      : {level.rows}x{level.columns}")
        print(f"Difficulty: {level.level}")
        print(f"Equations : {len(level.equations)}")
        print(f"Cells     : {len(level.cells)}")
        print(f"Tiles     : {level.numberTiles}")

if __name__ == "__main__":
    main()
