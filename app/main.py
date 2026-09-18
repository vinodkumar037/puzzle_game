# from app.generator import generate_level
# from app.nodes import generate_node

# def main():

#     state = {
#         "rows": 5,
#         "columns": 5,
#         "difficulty": "easy"
#     }

#     result = generate_node(state)
#     levels = result["levels"]

#     for level in levels:
#         print(level.model_dump_json(indent=2))


# if __name__ == "__main__":
#     main()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal

from app.graph import puzzle_graph
from app.schemas import Level

app = FastAPI(
    title="Puzzle Game API",
    description="Generates unique puzzles",
    version="1.0.0",
)

# Request schema
class GeneratePuzzleRequest(BaseModel):
    difficulty: Literal["easy", "medium", "hard"]
    rows: int = Field(ge=3, le=20)
    columns: int = Field(ge=3, le=20)

# Response schema
class GeneratePuzzleResponse(BaseModel):
    requested: int
    levels: list[Level]

@app.get("/")
def home():
    return {
        "message": "Puzzle Game API is running."
    }

@app.post("/generate-puzzles", response_model=GeneratePuzzleResponse)
def generate_puzzle(request: GeneratePuzzleRequest):

    initial_state = {
        "rows": request.rows,
        "columns": request.columns,
        "difficulty": request.difficulty,
    }

    try:
        result =  puzzle_graph.invoke(initial_state)

        return {
            "levels": result["levels"],
        }


    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Puzzle generation failed: {str(e)}",
        )
