import os
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
    rows: int = Field(ge=5, le=20)
    columns: int = Field(ge=5, le=20)

# Response schema
class GeneratePuzzleResponse(BaseModel):
    target_count: int
    valid_count: int
    attempts: int
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
        result = puzzle_graph.invoke(initial_state)
        valid_levels = result.get("levels", [])
        target_count = int(os.getenv("NUMBER_OF_LEVELS", "10"))

        return {
            "target_count": target_count,
            "valid_count": len(valid_levels),
            "attempts": result.get("generation_attempts", 1),
            "levels": valid_levels,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Puzzle generation failed: {str(e)}",
        )


