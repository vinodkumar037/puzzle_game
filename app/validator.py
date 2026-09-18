from app.schemas import Level, CellType, Operation
from app.database import check_level_duplicate

def get_effective_cell_value(cell) -> int:
    if cell.type == CellType.NUMBER:
        return cell.value
    elif cell.type == CellType.EMPTY:
        return cell.solution
    return None

def validate_level_logic(level: Level) -> list[str]:
    """
    Validate structural and mathematical logic of a level.
    Returns a list of error strings. If empty, the level is valid.
    """
    errors = []

    # 1. Grid boundary and CellType contract checks
    cell_map = {}
    for cell in level.cells:
        if cell.row < 0 or cell.row >= level.rows or cell.column < 0 or cell.column >= level.columns:
            errors.append(f"Cell at ({cell.row}, {cell.column}) is out of grid bounds ({level.rows}x{level.columns})")
        key = (cell.row, cell.column)
        if key in cell_map:
            errors.append(f"Duplicate cell position at ({cell.row}, {cell.column}).")
        cell_map[key] = cell

        # CellType attribute validation
        if cell.type == CellType.NUMBER:
            if cell.value < 0:
                errors.append(f"NUMBER Cell at ({cell.row}, {cell.column}) must have value >= 0.")
            if cell.solution != -1:
                errors.append(f"NUMBER Cell at ({cell.row}, {cell.column}) must have solution = -1.")
            if cell.text != str(cell.value):
                errors.append(f"NUMBER Cell at ({cell.row}, {cell.column}) text '{cell.text}' must match value '{cell.value}'.")

        elif cell.type == CellType.EMPTY:
            if cell.solution < 0:
                errors.append(f"EMPTY Cell at ({cell.row}, {cell.column}) must have solution >= 0.")
            if cell.value != -1:
                errors.append(f"EMPTY Cell at ({cell.row}, {cell.column}) must have value = -1.")
            if cell.text != "":
                errors.append(f"EMPTY Cell at ({cell.row}, {cell.column}) text must be '' (empty string).")

        elif cell.type == CellType.OPERATOR:
            if cell.value != -1 or cell.solution != -1:
                errors.append(f"OPERATOR Cell at ({cell.row}, {cell.column}) must have value = -1 and solution = -1.")
            if cell.text not in ["+", "-", "*", "/"]:
                errors.append(f"OPERATOR Cell at ({cell.row}, {cell.column}) invalid text '{cell.text}'. Must be '+', '-', '*', or '/'.")

        elif cell.type == CellType.EQUALS:
            if cell.value != -1 or cell.solution != -1:
                errors.append(f"EQUALS Cell at ({cell.row}, {cell.column}) must have value = -1 and solution = -1.")
            if cell.text.strip() != "=":
                errors.append(f"EQUALS Cell at ({cell.row}, {cell.column}) invalid text '{cell.text}'. Must be strictly '='.")
        else:
            errors.append(f"Cell at ({cell.row}, {cell.column}) has unknown type '{cell.type}'.")


    # 2. Equation checks
    if not level.equations:
        errors.append("Level has no equations.")

    for idx, eq in enumerate(level.equations):
        first_key = (eq.firstRow, eq.firstColumn)
        second_key = (eq.secondRow, eq.secondColumn)
        result_key = (eq.resultRow, eq.resultColumn)

        if first_key not in cell_map:
            errors.append(f"Equation {idx}: First operand cell missing at {first_key}.")
            continue
        if second_key not in cell_map:
            errors.append(f"Equation {idx}: Second operand cell is missing at {second_key}.")
            continue
        if result_key not in cell_map:
            errors.append(f"Equation {idx}: result cell is missing at {result_key}.")
            continue

        val1 = get_effective_cell_value(cell_map[first_key])
        val2 = get_effective_cell_value(cell_map[second_key])
        res = get_effective_cell_value(cell_map[result_key])

        if val1 is None or val2 is None or res is None:
            errors.append(f"Equation {idx}: Operand/Result must be NUMBER or EMPTY cells.")
            continue

        op = eq.operation
        valid_math = False

        if op == Operation.ADDITION:
            valid_math = (val1 + val2 == res)
            op_symbol = "+"
        elif op == Operation.SUBTRACTION:
            valid_math = (val1 - val2 == res)
            op_symbol = "-"
        elif op == Operation.MULTIPLICATION:
            valid_math = (val1 * val2 == res)
            op_symbol = "*"
        elif op == Operation.DIVISION:
            valid_math = (
                val2 != 0
                and val1 % val2 == 0
                and val1 // val2 == res
            )
            op_symbol = "/"
        else:
            errors.append(f"Equation {idx}: Unknown operation {op}.")
            continue

        if not valid_math:
            errors.append(
                f"Equation {idx} math mismatch: {val1} {op_symbol} {val2} != {res}"
            )

    # 3. number tiles check
    if any(tile < 0 for tile in level.numberTiles):
        errors.append("numberTiles must contain only non-negative values.") 

    if len(level.numberTiles) < 3:
        errors.append(f"numberTiles must contain at least 3 tiles, but got {len(level.numberTiles)}.")

    empty_solutions = [c.solution for c in level.cells if c.type == CellType.EMPTY]
    for sol in empty_solutions:
        if sol not in level.numberTiles:
            errors.append(f"Solution value {sol} is missing from numberTiles {level.numberTiles}.")

    return errors


def validate_level_against_db(level: Level) -> str | None:
    """
    Checks if the level is a duplicate in the database.
    Returns error string if duplicate, None otherwise.
    """
    if check_level_duplicate(level):
        return "Duplicate level structure found in database."
    return None