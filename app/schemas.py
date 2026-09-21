from enum import IntEnum
from pydantic import BaseModel, Field
from typing import Literal


class CellType(IntEnum):
    NUMBER = 1
    EMPTY = 2
    OPERATOR = 3
    EQUALS = 4


class Cell(BaseModel):
    row: int = Field(..., description="Row index of the cell (0-indexed)")
    column: int = Field(..., description="Column index of the cell (0-indexed)")
    type: CellType = Field(..., description="Type of the cell: 1=NUMBER, 2=EMPTY, 3=OPERATOR, 4=EQUALS")
    text: str = Field(..., description="Text content of the cell: str(value) for NUMBER, '' for EMPTY, operator symbol ('+', '-', '*', '/') for OPERATOR, '=' for EQUALS")
    value: int = Field(..., description="Numeric value >= 0 for NUMBER cell; -1 for EMPTY, OPERATOR, and EQUALS cells")
    solution: int = Field(..., description="Correct answer >= 0 for EMPTY cell; -1 for NUMBER, OPERATOR, and EQUALS cells")



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
    level: Literal["easy", "medium", "hard"]
    rows: int
    columns: int

    cells: list[Cell] = Field(..., min_length=5, max_length=25, description="Sparse list of grid cells (between 5 and 25 cells total)")
    equations: list[Equation] = Field(..., min_length=1, max_length=10, description="List of equations (1 to 10 equations)")
    numberTiles: list[int] = Field(..., min_length=3, max_length=15, description="List of available answer tiles (at least 3 tiles)")

