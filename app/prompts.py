def build_generation_prompt(
    rows: int,
    columns: int,
    difficulty: str,
    rules: dict,
) -> str:

    return f"""
Generate ONE arithmetic puzzle level.

Level number:

Grid dimensions:
{rows} rows × {columns} columns

Difficulty:
{difficulty}

Difficulty rules:
{rules}

IMPORTANT GRID RULE:

The grid dimensions define the maximum coordinate boundaries.

They DO NOT mean that every grid position must have a cell.

Cells are SPARSE.

Only create Cell objects for positions that are actually
part of an equation.

Do NOT generate all {rows * columns} cells.

For example, for a 5 × 5 grid, it is NOT required to create
25 Cell objects.

A valid puzzle may use only a small subset of the available
grid coordinates.

CELL RULES:

- type 1 = fixed number
- type 2 = empty number that the player must solve
- type 3 = mathematical operator
- type 4 = equals sign (=)

For fixed numbers:
- text contains the displayed number
- value contains the numeric value
- solution must be -1

For empty number cells:
- text should be ""
- value should be -1
- solution contains the correct answer

For operators:
- text contains the operator
- value = -1
- solution = -1

For equals:
- text = "="
- value = -1
- solution = -1

EQUATION RULES:

Each equation references existing cells.

firstRow/firstColumn identify the first operand.

secondRow/secondColumn identify the second operand.

resultRow/resultColumn identify the result.

operation:
0 = addition
1 = subtraction
2 = multiplication
3 = division

Every equation must be mathematically correct.

NUMBER TILE RULES:

numberTiles should contain the available answer tiles
for the empty number cells.

The correct solutions must be included.

Do not generate duplicate unnecessary cells.

Return exactly ONE Level object.
"""
