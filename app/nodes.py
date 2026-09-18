import os
from app.generator import generate_level
from app.validator import validate_level_logic, validate_level_against_db
from app.database import compute_level_fingerprint, save_level_to_db


def generate_node(state):
    target_count = int(os.getenv("NUMBER_OF_LEVELS", "10"))
    existing_levels = state.get("levels") or []
    needed_count = max(0, target_count - len(existing_levels))
    attempts = state.get("generation_attempts", 0) + 1
    validation_errors = state.get("validation_errors") or []

    candidates = []
    if needed_count > 0:
        for _ in range(needed_count):
            try:
                level = generate_level(
                    rows=state["rows"],
                    columns=state["columns"],
                    difficulty=state["difficulty"],
                    validation_errors=validation_errors,
                )
                candidates.append(level)
                from pprint import pprint
                pprint(candidates)
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

    # Keep track of fingerprints of already validated levels
    existing_fps = {compute_level_fingerprint(lvl) for lvl in accumulated_levels}

    for level in candidates:
        # 1. Structural and math logic validation
        logic_errors = validate_level_logic(level)
        if logic_errors:
            err_msg = f"Attempt {state.get('generation_attempts')}: Logic errors - {'; '.join(logic_errors)}"
            print(f"[Validate Node] {err_msg}")
            validation_errors.append(err_msg)
            continue

        # 2. Database duplicate check
        db_err = validate_level_against_db(level)
        if db_err:
            err_msg = f"Attempt {state.get('generation_attempts')}: DB duplicate - {db_err}"
            print(f"[Validate Node] {err_msg}")
            validation_errors.append(err_msg)
            continue

        # 3. Batch duplicate check against current accumulated levels
        fp = compute_level_fingerprint(level)
        if fp in existing_fps:
            err_msg = f"Attempt {state.get('generation_attempts')}: Batch duplicate level generated."
            print(f"[Validate Node] {err_msg}")
            validation_errors.append(err_msg)
            continue

        # Level passed all checks
        existing_fps.add(fp)
        accumulated_levels.append(level)

    return {
        "levels": accumulated_levels,
        "validation_errors": validation_errors,
    }


def save_node(state):
    valid_levels = state.get("levels") or []
    saved_count = 0

    for level in valid_levels:
        if save_level_to_db(level):
            saved_count += 1

    print(f"[Save Node] Saved {saved_count}/{len(valid_levels)} levels to MongoDB.")
    return {
        "levels": valid_levels
    }

# def save_node(state):
#     valid_levels = state.get("levels") or []
#     target_count = int(os.getenv("NUMBER_OF_LEVELS", "10"))

#     # Do not save an incomplete batch.
#     # if len(valid_levels) < target_count:
#     #     raise ValueError(
#     #         f"Cannot save: generated {len(valid_levels)}/{target_count} levels."
#     #     )

#     # Final validation before writing to the database.
#     for index, level in enumerate(valid_levels):
#         errors = validate_level_logic(level)
#         if errors:
#             raise ValueError(
#                 f"Cannot save invalid level {index + 1}: {'; '.join(errors)}"
#             )

#     saved_count = 0

#     for level in valid_levels:
#         if save_level_to_db(level):
#             saved_count += 1

#     print(f"[Save Node] Saved {saved_count}/{len(valid_levels)} levels to MongoDB.")

#     return {"levels": valid_levels}



