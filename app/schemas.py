from enum import IntEnum
from pydantic import BaseModel, Field
from typing import Literal


class CellType(IntEnum):
    NUMBER = 1
    EMPTY = 2
    OPERATOR = 3
    EQUALS = 4


class Cell(BaseModel):
    row: int = Field(..., description="Row index of the cell")
    column: int = Field(..., description="Column index of the cell")
    type: CellType = Field(..., description="Type of the cell")
    text: str = Field(..., description="Text content of the cell")
    value: int = Field(..., description="Numeric value of the cell")
    solution: int = Field(..., description="Solution value of the cell")


class Operation(IntEnum):
    ADDITION = 0
    SUBTRACTION = 1
    MULTIPLICATION = 2
    DIVISION = 3


class Equation(BaseModel):
    firstRow: int
    firstColumn: int

    secondRow: int
    secondColumn: int

    resultRow: int
    resultColumn: int

    operation: Operation


class Level(BaseModel):
    level: Literal["eassy", "medium", "hard"]
    rows: int
    columns: int

    cells: list[Cell]
    equations: list[Equation]
    numberTiles: list[int]


class PuzzleRequest(BaseModel):
    rows: int = Field(ge=3, le=20)
    columns: int = Field(ge=3, le=20)
    difficulty: Literal["easy", "medium", "hard"] = Field(..., description="Difficulty level of the puzzle")