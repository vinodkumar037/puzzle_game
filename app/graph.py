import os
from langgraph.graph import StateGraph, START, END
from app.state import PuzzleState
from app.nodes import generate_node, validate_node, save_node


def should_continue(state: PuzzleState) -> str:
    target_count = int(os.getenv("NUMBER_OF_LEVELS", "10"))
    valid_levels = state.get("levels") or []
    attempts = state.get("generation_attempts", 0)
    max_attempts = int(os.getenv("MAX_ATTEMPTS", "5"))

    if len(valid_levels) < target_count and attempts < max_attempts:
        print(f"[Graph Routing] Attempt {attempts}: {len(valid_levels)}/{target_count} valid levels. Retrying generation...")
        return "generate"

    return "save"



def build_puzzle_graph():
    workflow = StateGraph(PuzzleState)

    workflow.add_node("generate", generate_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("save", save_node)

    workflow.add_edge(START, "generate")
    workflow.add_edge("generate", "validate")
    workflow.add_conditional_edges(
        "validate",
        should_continue,
        {
            "generate": "generate",
            "save": "save",
        }
    )
    workflow.add_edge("save", END)

    return workflow.compile()

puzzle_graph = build_puzzle_graph()