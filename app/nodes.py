import os
from app.generator import generate_level
from app.validator import validate_level_logic, validate_level_against_db
from app.database import compute_level_fingerprint, save_level_to_db
from app.schemas import CellType


def format_level_summary(level) -> str:
    return str(level)




def generate_node(state):
    target_count = int(os.getenv("NUMBER_OF_LEVELS", "10"))
    existing_levels = state.get("levels") or []
    needed_count = max(0, target_count - len(existing_levels))
    attempts = state.get("generation_attempts", 0) + 1
    validation_errors = state.get("validation_errors") or []
    excluded_puzzles = state.get("excluded_puzzles") or []

    candidates = []
    if needed_count > 0:
        for _ in range(needed_count):
            try:
                level = generate_level(
                    rows=state["rows"],
                    columns=state["columns"],
                    difficulty=state["difficulty"],
                    validation_errors=validation_errors,
                    excluded_puzzles=excluded_puzzles,
                )
                candidates.append(level)
                print(f"=====================================candidates========================{level}")
            except Exception as e:
                raise RuntimeError(f"Level generation failed: {e}") from e

    return {
        "candidate_levels": candidates,
        "generation_attempts": attempts,
    }


def validate_node(state):
    candidates = state.get("candidate_levels") or []
    accumulated_levels = list(state.get("levels") or [])
    validation_errors = []

    # Memory retained across the graph iterations
    seen_fps = set(state.get("seen_fingerprints") or [])
    excluded_puzzles = list(state.get("excluded_puzzles") or [])

    # Include fingerprints of all already accepted levels
    seen_fps.update(
        compute_level_fingerprint(level)
        for level in accumulated_levels
    )

    for level in candidates:
        summary = format_level_summary(level)
        fp = compute_level_fingerprint(level)

        # 1. Batch & Cross-Run Duplicate Check
        if fp in seen_fps:
            validation_errors.append(f"Batch/Run duplicate puzzle: {fp}")
            if summary not in excluded_puzzles:
                excluded_puzzles.append(summary)
            continue

        # 2. Structural and math logic validation
        logic_errors = validate_level_logic(level)
        if logic_errors:
            validation_errors.append(f"Logic errors: {'; '.join(logic_errors)}")
            if summary not in excluded_puzzles:
                excluded_puzzles.append(summary)
            seen_fps.add(fp)
            continue

        # 3. Database duplicate check
        db_err = validate_level_against_db(level)
        if db_err:
            err_msg = f"Attempt {state.get('generation_attempts')}: DB duplicate - {db_err}"
            print(f"[Validate Node] {err_msg}")
            validation_errors.append(err_msg)
            if summary not in excluded_puzzles:
                excluded_puzzles.append(summary)
            seen_fps.add(fp)
            continue

        # Level passed all checks
        seen_fps.add(fp)
        accumulated_levels.append(level)
        if summary not in excluded_puzzles:
            excluded_puzzles.append(summary)

    return {
        "levels": accumulated_levels,
        "validation_errors": validation_errors,
        "excluded_puzzles": excluded_puzzles,
        "seen_fingerprints": list(seen_fps),
    }


def save_node(state):
    valid_levels = state.get("levels") or []
    target_count = int(os.getenv("NUMBER_OF_LEVELS", "10"))
    saved_count = 0

    for level in valid_levels:
        if save_level_to_db(level):
            saved_count += 1

    if len(valid_levels) < target_count:
        print(f"[Save Node Warning] Saved {saved_count}/{len(valid_levels)} valid levels (target was {target_count}).")
    else:
        print(f"[Save Node] Successfully saved {saved_count}/{len(valid_levels)} levels to MongoDB.")

    return {
        "levels": valid_levels
    }
