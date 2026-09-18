FEW_SHOT_EXAMPLES = """
EXAMPLE 1 — Valid easy level

The following is an example of the exact required Level JSON structure.
It represents the equation 3 + 4 = 7.

{
  "level": "easy",
  "rows": 5,
  "columns": 5,
  "cells": [
    {"row": 0, "column": 0, "type": 1, "text": "3", "value": 3, "solution": -1},
    {"row": 0, "column": 1, "type": 3, "text": "+", "value": -1, "solution": -1},
    {"row": 0, "column": 2, "type": 2, "text": "", "value": -1, "solution": 4},
    {"row": 0, "column": 3, "type": 4, "text": "=", "value": -1, "solution": -1},
    {"row": 0, "column": 4, "type": 1, "text": "7", "value": 7, "solution": -1}
  ],
  "equations": [
    {
      "firstRow": 0,
      "firstColumn": 0,
      "secondRow": 0,
      "secondColumn": 2,
      "resultRow": 0,
      "resultColumn": 4,
      "operation": 0
    }
  ],
  "numberTiles": [2, 4, 5]
}

IMPORTANT:
- This is one Level object, not an object containing a "levels" array.
- Use "level", not "levelNumber".
- Every cell position must be unique.
- Every EQUALS cell must have text "=".
- Every equation must be mathematically correct.
- Every equation coordinate must reference an existing NUMBER or EMPTY cell.
- EMPTY cells must have text="", value=-1, and solution equal to the correct answer.
- NUMBER cells must have text equal to their value and solution=-1.
- OPERATOR and EQUALS cells must have value=-1 and solution=-1.
- Use the example to learn the structure, not to copy its exact puzzle.
"""

def build_generation_prompt(
    rows: int,
    columns: int,
    difficulty: str,
    rules: dict,
    validation_errors: list[str] | None = None,
) -> str:

    feedback_section = ""

    if validation_errors:
        formatted_errors = "\n".join(
            f"- {err}" for err in validation_errors[-10:]
        )

        feedback_section = f"""
            PREVIOUS GENERATION FAILED VALIDATION.

            These are the exact errors. Fix every one of them:
            {formatted_errors}

            Do not repeat these mistakes.
            Regenerate the ENTIRE level and recheck every field.
            """

    return f"""
        You are generating ONE valid arithmetic puzzle level.

        You must follow every rule below.
        Correctness is more important than creativity.

        GRID:
        - Rows: {rows}
        - Columns: {columns}
        - Difficulty: {difficulty}
        - Difficulty rules: {rules}

        {feedback_section}

        ==================================================
        1. GRID AND CELL RULES
        ==================================================

        The grid is sparse. Do not create cells for unused positions.

        Every cell coordinate must satisfy:
        0 <= row < {rows}
        0 <= column < {columns}

        Do not create duplicate cells at the same coordinate.

        Cell types and exact field values:

        NUMBER (type=1):
        - text must equal str(value)
        - value must be >= 0
        - solution must be -1

        EMPTY (type=2):
        - text must be exactly ""
        - value must be -1
        - solution must be the correct answer, >= 0

        OPERATOR (type=3):
        - text must be exactly one of: "+", "-", "*", "/"
        - value must be -1
        - solution must be -1

        EQUALS (type=4):
        - text must be exactly "="
        - value must be -1
        - solution must be -1

        IMPORTANT:
        The equals sign is exactly one character: "=".

        These are INVALID:
        - "1"
        - " "
        - ""
        - "=="
        - " = "
        - "\\u003d"

        Never use any of those values for an EQUALS cell.

        Before returning the level, inspect every cell with type=4.
        For each one, verify that text == "=".

        ==================================================
        2. EQUATION RULES
        ==================================================

        Every equation must reference existing cells.

        The first operand, second operand, and result must each
        reference a cell of type NUMBER or EMPTY.

        The equation's operation must match its operation enum:
        0 = addition
        1 = subtraction
        2 = multiplication
        3 = division

        Every equation must be mathematically correct.

        For each equation:
        - Read the operand's value if it is NUMBER.
        - Read the operand's solution if it is EMPTY.
        - Calculate the result using the specified operation.
        - Compare it with the result cell's value or solution.

        The calculated result must equal the result cell's answer.

        Do not create equations with missing referenced cells.
        Do not use an operator or equals cell as an operand or result.

        ==================================================
        3. NUMBER TILES — CRITICAL
        ==================================================

        numberTiles is the list of answer tiles available to the player
        for filling ALL EMPTY cells.

        Follow these rules:

        1. Find every cell whose type is EMPTY.
        2. Collect the solution of EVERY EMPTY cell.
        3. Every empty-cell solution must appear in numberTiles.
        4. Do not return only the first answer.
        5. Do not omit answers for other empty cells.
        6. Do not include -1 or invalid values.
        7. Preserve repeated answers when multiple EMPTY cells have.
        8. numberTiles MUST contain at least 3 tiles (len(numberTiles) >= 3). Add distractor tiles if there are fewer than 3 empty cells.
        the same solution, if each empty cell needs its own tile.

        If there are N EMPTY cells and the game uses exactly one tile
        per empty cell, numberTiles must contain exactly N tiles.

        Example:
        EMPTY solutions: [4, 7, 2]
        Valid numberTiles: [4, 7, 2]

        Invalid numberTiles: [4]
        Invalid numberTiles: [4, 7]
        Invalid numberTiles: [4, 7, 2, 9]  # if no distractors are allowed

        If the game supports distractor tiles, include all correct
        answers plus the required number of extra, non-negative tiles.
        Never replace or omit a correct answer with a distractor.

        ==================================================
        4. FINAL SELF-CHECK
        ==================================================

        Before returning the level, verify:

        - The level difficulty is "{difficulty}".
        - Grid dimensions are correct.
        - Every cell coordinate is within bounds.
        - No duplicate cell coordinates exist.
        - Every cell's type, text, value, and solution are consistent.
        - Every EQUALS cell has text exactly "=".
        - Every equation references existing cells.
        - Every equation is mathematically correct.
        - Every EMPTY cell's solution is included in numberTiles.
        - numberTiles contains all required answers.
        - No invalid or unnecessary cells are present.

        If any check fails, fix the level before returning it.

        Return exactly ONE Level object matching the required schema.
        Do not return explanations or markdown.
        {FEW_SHOT_EXAMPLES}
        """