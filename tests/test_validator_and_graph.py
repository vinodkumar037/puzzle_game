import pytest
from app.schemas import Level, Cell, CellType, Equation, Operation
from app.validator import validate_level_logic, validate_level_against_db
from app.database import compute_level_fingerprint
from app.graph import should_continue, puzzle_graph


def create_sample_valid_level():
    # 2 + 3 = 5
    cells = [
        Cell(row=0, column=0, type=CellType.NUMBER, text="2", value=2, solution=-1),
        Cell(row=0, column=1, type=CellType.OPERATOR, text="+", value=-1, solution=-1),
        Cell(row=0, column=2, type=CellType.NUMBER, text="3", value=3, solution=-1),
        Cell(row=0, column=3, type=CellType.EQUALS, text="=", value=-1, solution=-1),
        Cell(row=0, column=4, type=CellType.EMPTY, text="", value=-1, solution=5),
    ]
    equations = [
        Equation(
            firstRow=0, firstColumn=0,
            secondRow=0, secondColumn=2,
            resultRow=0, resultColumn=4,
            operation=Operation.ADDITION
        )
    ]
    return Level(
        level="easy",
        rows=5,
        columns=5,
        cells=cells,
        equations=equations,
        numberTiles=[5, 10, 15]
    )


def test_validate_level_logic_valid():
    level = create_sample_valid_level()
    errors = validate_level_logic(level)
    assert errors == []


def test_validate_level_logic_math_error():
    level = create_sample_valid_level()
    # Change solution to wrong number 99 (2 + 3 != 99)
    level.cells[4].solution = 99
    level.numberTiles = [99]
    errors = validate_level_logic(level)
    assert len(errors) > 0
    assert any("math mismatch" in err for err in errors)


def test_validate_level_logic_number_tiles_count():
    level = create_sample_valid_level()
    level.numberTiles = [5, 10]  # Only 2 tiles (< 3)
    errors = validate_level_logic(level)
    assert len(errors) > 0
    assert any("at least 3 tiles" in err for err in errors)



def test_validate_level_logic_out_of_bounds():
    level = create_sample_valid_level()
    level.cells[0].row = 10  # Out of bounds for 5x5 grid
    errors = validate_level_logic(level)
    assert len(errors) > 0
    assert any("out of grid bounds" in err for err in errors)


def test_validate_level_logic_cell_type_formatting():
    # EQUALS cell with padded spaces " = " should fail
    level = create_sample_valid_level()
    level.cells[3].text = " = "
    errors = validate_level_logic(level)
    assert len(errors) > 0
    assert any("EQUALS Cell" in err and "Must be strictly '='" in err for err in errors)

    # OPERATOR cell with invalid text " + " should fail
    level_op = create_sample_valid_level()
    level_op.cells[1].text = " + "
    errors_op = validate_level_logic(level_op)
    assert len(errors_op) > 0
    assert any("OPERATOR Cell" in err for err in errors_op)

    # EMPTY cell with non-empty text "5" should fail
    level_empty = create_sample_valid_level()
    level_empty.cells[4].text = "5"
    errors_empty = validate_level_logic(level_empty)
    assert len(errors_empty) > 0
    assert any("EMPTY Cell" in err for err in errors_empty)


def test_compute_level_fingerprint_deterministic():
    level1 = create_sample_valid_level()
    level2 = create_sample_valid_level()
    fp1 = compute_level_fingerprint(level1)
    fp2 = compute_level_fingerprint(level2)
    assert fp1 == fp2
    assert isinstance(fp1, str) and len(fp1) == 64  # SHA256 hex string


def test_build_generation_prompt_with_feedback():
    from app.prompts import build_generation_prompt
    errors = ["EQUALS Cell at (1, 0) invalid text ''. Must be strictly '='."]
    prompt = build_generation_prompt(rows=5, columns=5, difficulty="easy", rules={}, validation_errors=errors)
    assert "PREVIOUS GENERATION FAILED VALIDATION" in prompt
def test_validate_node_retains_excluded_puzzles_and_fingerprints():
    from app.nodes import validate_node
    level = create_sample_valid_level()
    state = {
        "candidate_levels": [level],
        "levels": [],
        "validation_errors": [],
        "excluded_puzzles": [],
        "seen_fingerprints": [],
        "generation_attempts": 1,
    }
    result = validate_node(state)
    assert "excluded_puzzles" in result
    assert "seen_fingerprints" in result
    assert len(result["excluded_puzzles"]) == 1
    assert len(result["seen_fingerprints"]) == 1
    assert "rows=5" in result["excluded_puzzles"][0]







def test_should_continue_retry_condition(monkeypatch):
    monkeypatch.setenv("NUMBER_OF_LEVELS", "3")
    # If valid levels < requested, continue to generate
    state = {
        "levels": [create_sample_valid_level()],
        "generation_attempts": 1,
        "max_attempts": 5
    }
    assert should_continue(state) == "generate"

    # If valid levels >= requested, proceed to save
    monkeypatch.setenv("NUMBER_OF_LEVELS", "1")
    state_done = {
        "levels": [create_sample_valid_level()],
        "generation_attempts": 1,
        "max_attempts": 5
    }
    assert should_continue(state_done) == "save"

    # If max attempts reached, proceed to save
    monkeypatch.setenv("NUMBER_OF_LEVELS", "5")
    state_max_attempts = {
        "levels": [create_sample_valid_level()],
        "generation_attempts": 5,
        "max_attempts": 5
    }
    assert should_continue(state_max_attempts) == "save"

