from pymongo import MongoClient
import os
from dotenv import load_dotenv
from app.schemas import Level

load_dotenv()

uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
try:
    client = MongoClient(uri, serverSelectionTimeoutMS=2000)
    client.admin.command('ping')
    db = client[os.getenv("MONGODB_DB_NAME", "puzzle_game")]
    puzzle_game = db["puzzle_game"]
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Error connecting to MongoDB: {str(e)}")

def compute_level_fingerprint(level: Level) -> str:
    import hashlib
    import json

    cells_data = sorted(
        [{"r": c.row, "c": c.column, "t": c.type, "v": c.value, "sol": c.solution, "txt": c.text} for c in level.cells],
        key=lambda x: (x["r"], x["c"])
    )
    eqs_data = sorted(
        [{
            "fr": e.firstRow, "fc": e.firstColumn,
            "sr": e.secondRow, "sc": e.secondColumn,
            "rr": e.resultRow, "rc": e.resultColumn,
            "op": int(e.operation)
        } for e in level.equations],
        key=lambda x: (x["fr"], x["fc"], x["sr"], x["sc"], int(x["op"]))
    )
    data = {
        "rows": level.rows,
        "cols": level.columns,
        "cells": cells_data,
        "equations": eqs_data
    }
    canonical = json.dumps(data, sort_keys=True)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def check_level_duplicate(level: Level) -> bool:
    if puzzle_game is None:
        # If DB connection is not available, assume non-duplicate
        return False

    fp = compute_level_fingerprint(level)
    existing = puzzle_game.find_one({"fingerprint": fp})
    return existing is not None


def save_level_to_db(level: Level) -> bool:
    if puzzle_game is None:
        return False

    fp = compute_level_fingerprint(level)
    level_doc = level.model_dump()
    level_doc["fingerprint"] = fp

    # Upsert or insert
    puzzle_game.update_one(
        {"fingerprint": fp},
        {"$set": level_doc},
        upsert=True
    )
    return True
