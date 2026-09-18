from langgraph.graph import StateGraph, START, END
from app.state import PuzzleState
from app.nodes import generate_node

def build_puzzle_graph():
    workflow = StateGraph(PuzzleState)

    workflow.add_node("generate", generate_node)

    workflow.add_edge(START, "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()

puzzle_graph = build_puzzle_graph()