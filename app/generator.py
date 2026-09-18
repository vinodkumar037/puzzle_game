import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().with_name(".env"))


def _get_structured_llm():
    from langchain.chat_models import init_chat_model

    from app.schemas import Level

    model_name = (os.getenv("LLM_MODEL") or "gpt-4o-mini").strip()
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    api_key = os.getenv("GOOGLE_API_KEY")

    llm = init_chat_model(
        model=model_name, 
        model_provider="google_genai",
        api_key=api_key,
        temperature=temperature)
    
    return llm.with_structured_output(Level)


def generate_level(
        rows: int,
        columns: int,
        difficulty: str
):
    from app.prompts import build_generation_prompt
    from app.rules import get_difficulty_roles
    from app.schemas import Level

    rules = get_difficulty_roles(difficulty)

    prompt = build_generation_prompt(
        rows=rows,
        columns=columns,
        difficulty=difficulty,
        rules=rules,
    )

    structured_llm = _get_structured_llm()
    result = structured_llm.invoke(prompt)
    if not isinstance(result, Level):
        return Level.model_validate(result)
    return result
