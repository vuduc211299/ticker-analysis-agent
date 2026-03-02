"""LangGraph crypto-analysis pipeline — graph wiring & CLI entry point."""

from __future__ import annotations

import argparse
import logging

from typing import cast

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from nodes import AgentState, analyzer_node, extract_ticker, fetch_api_data, reporter_node

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
log = logging.getLogger(__name__)


# ─── LangGraph Pipeline (compiled once at module level) ──────────────────────

def _build_graph() -> CompiledStateGraph:
    graph = StateGraph(AgentState)
    graph.add_node("extract_ticker", extract_ticker)
    graph.add_node("fetch_api_data", fetch_api_data)
    graph.add_node("analyzer_node", analyzer_node)
    graph.add_node("reporter_node", reporter_node)

    graph.set_entry_point("extract_ticker")
    graph.add_edge("extract_ticker", "fetch_api_data")
    graph.add_edge("fetch_api_data", "analyzer_node")
    graph.add_edge("analyzer_node", "reporter_node")
    graph.add_edge("reporter_node", END)

    return graph.compile()


_APP = _build_graph()


def run_agent(user_input: str) -> AgentState:
    """Run the full pipeline and return the final state."""
    initial_state: AgentState = {
        "user_input": user_input,
        "errors": [],
    }
    return cast(AgentState, _APP.invoke(initial_state))


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="LangGraph crypto analysis bot — real API + LLM analysis pipeline.",
    )
    parser.add_argument("query", nargs="*", help="User request text")
    args = parser.parse_args()

    query = " ".join(args.query).strip() or input("Enter your request: ").strip()

    print("=" * 60)
    print("Starting crypto analysis pipeline...")
    print("=" * 60)

    final_state = run_agent(query)

    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(final_state.get("report", "No report generated."))

    errors = final_state.get("errors", [])
    if errors:
        print("\n--- Warnings / Errors ---")
        for err in errors:
            print(f"  ⚠ {err}")
