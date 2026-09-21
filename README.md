# Puzzle Agent (v1.0.0)

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12%2B-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141-teal)
![LangGraph](https://img.shields.io/badge/LangGraph-1.2-orange)

An autonomous AI agent framework designed to generate, validate, deduplicate, and persist arithmetic grid puzzle levels using **LangGraph**, **LangChain**, **Google Gemini GenAI**, **FastAPI**, and **MongoDB**.

---

## 🚀 Features

- **Autonomous Generation Graph**: Built with **LangGraph** orchestrating a multi-node workflow (`generate_node` ➔ `validate_node` ➔ `save_node` / retry feedback loop).
- **Strict Logic & Math Validation**: Validates grid bounds, cell type contracts, cell text, equation arithmetic correctness, and minimum number tiles (`len(numberTiles) >= 3`).
- **Database Fingerprinting & Deduplication**: Computes SHA-256 fingerprint hashes for generated levels to ensure zero duplicates across runs in **MongoDB**.
- **LLM Self-Correction**: Passes validation errors and previously generated level histories (`excluded_puzzles`) back into the prompt on retries to guide the LLM.
- **REST API Interface**: Production-ready FastAPI web service endpoint for level generation.

---

## 📁 Repository Structure

```text
puzzle_agent/
├── app/
│   ├── database.py       # MongoDB storage & fingerprint deduplication
│   ├── generator.py      # LLM structured output invocation
│   ├── graph.py          # LangGraph state graph definition & conditional routing
│   ├── main.py           # FastAPI web application & REST endpoints
│   ├── nodes.py          # LangGraph nodes (generate, validate, save)
│   ├── prompts.py        # System prompt templates & feedback injection
│   ├── rules.py          # Difficulty configurations (easy, medium, hard)
│   ├── schemas.py        # Pydantic data models (Level, Cell, Equation)
│   ├── state.py          # LangGraph state definition (PuzzleState)
│   └── validator.py      # Structural & mathematical logic validation rules
├── tests/
│   ├── test_generator_import.py
│   ├── test_graph.py
│   └── test_validator_and_graph.py
├── main.py               # Application entry point
├── pyproject.toml        # Project dependencies & package metadata
└── README.md             # Documentation
```

---

## 🛠️ Prerequisites

- **Python**: `>= 3.12`
- **Package Manager**: [`uv`](https://github.com/astral-sh/uv) (recommended) or standard `pip`
- **Database**: MongoDB running locally (default: `mongodb://localhost:27017`)
- **API Key**: Google Gemini API key (`GOOGLE_API_KEY`)

---

## ⚙️ Environment Setup

Create an `.env` file in the project root or inside `app/.env`:

```env
GOOGLE_API_KEY=your_google_gemini_api_key
LLM_MODEL=gemini-2.5-flash
LLM_TEMPERATURE=0.7
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=PUZZLE_GAME
MAX_ATTEMPTS=5
NUMBER_OF_LEVELS=5
```

---

## 💻 Commands to Execute

### 1. Install Dependencies

Using `uv` (recommended):
```bash
uv sync
```

Using standard `pip`:
```bash
pip install -e .
```

---

### 2. Start the FastAPI Web Server

Run the server with Uvicorn:
```bash
uvicorn app.main:app --reload --port 8000
```
Or using `uv`:
```bash
uv run uvicorn app.main:app --reload --port 8000
```

Once running, interactive API docs are available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

### 3. Generate Puzzles via REST API

Send a `POST` request to `/generate-puzzles`:

```bash
curl -X POST "http://127.0.0.1:8000/generate-puzzles" \
     -H "Content-Type: application/json" \
     -d '{
           "difficulty": "easy",
           "rows": 5,
           "columns": 5
         }'
```

**Sample API Response:**
```json
{
  "target_count": 5,
  "valid_count": 5,
  "attempts": 1,
  "levels": [
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
          "firstRow": 0, "firstColumn": 0,
          "secondRow": 0, "secondColumn": 2,
          "resultRow": 0, "resultColumn": 4,
          "operation": 0
        }
      ],
      "numberTiles": [2, 4, 5]
    }
  ]
}
```

---

### 4. Run Unit Tests

Execute unit test suite with `pytest`:
```bash
uv run pytest
```

To run specific test files:
```bash
uv run pytest tests/test_validator_and_graph.py tests/test_generator_import.py
```

---

### 5. Run Graph Integration Test

To invoke the LangGraph pipeline directly via Python script:
```bash
python tests/test_graph.py
```

---

## 🏷️ Version History

- **v1.0.0**: 
  - Complete LangGraph retry and feedback loop implementation.
  - Strict cell validation (`CellType` values, text constraints, minimum number tile enforcement).
  - Database SHA-256 fingerprint duplicate prevention.
  - FastAPI server integration (`/generate-puzzles`).
