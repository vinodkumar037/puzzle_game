from typing import TypedDict
from app.schemas import Level

class PuzzleState(TypedDict):
    rows: int
    columns: int
    difficulty: str
    number_of_levels: int
    levels: list[Level]
    validation_errors: list[str] | None
    generation_attempts: int



