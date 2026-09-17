from app.generator import generate_level
from app.nodes import generate_node

def main():

    state = {
        "rows": 5,
        "columns": 5,
        "difficulty": "easy"
    }

    result = generate_node(state)
    levels = result["levels"]

    for level in levels:
        print(level.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
