from typing import TypedDict
from app.schemas import Level

class PuzzleState(TypedDict, total=False):
    rows: int
    columns: int
    difficulty: str
    levels: list[Level]  # Puzzles ready to save to DB
    candidate_levels: list[Level] # New generated Puzzles
    validation_errors: list[str]
    generation_attempts: int
    max_attempts: int





