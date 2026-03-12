"""Integration evaluation for Website + University Cost MCP + Graph MCP bridge."""

from __future__ import annotations

import json
import requests

BASE_URL = "http://127.0.0.1:5055"

PROMPTS = [
    "Im planning to go to Rutgers New Brunswick for a Masters, what do the costs look like?",
    "Compare MIT and Stanford master's costs and show me the graph.",
    "Show me a projection chart for bachelor's vs master's outcomes.",
    "What does Oxford cost for a master's degree?",
]


def check_health() -> None:
    response = requests.get(f"{BASE_URL}/api/health", timeout=10)
    response.raise_for_status()
    payload = response.json()
    assert payload.get("ok") is True
    print("[PASS] Health endpoint reachable")


def evaluate_prompt(prompt: str) -> None:
    response = requests.post(
        f"{BASE_URL}/api/advisor",
        json={"prompt": prompt},
        timeout=45,
    )
    response.raise_for_status()
    payload = response.json()

    assert isinstance(payload.get("answer"), str) and payload["answer"].strip(), "Missing answer text"
    assert payload.get("mcp", {}).get("graph", {}).get("used") is True, "Graph MCP should be used"
    assert isinstance(payload.get("graph", {}).get("html"), str) and payload["graph"]["html"].strip(), "Missing graph html"

    if "Rutgers" in prompt:
        mode = payload.get("mcp", {}).get("universityCost", {}).get("mode")
        assert mode in {"get_university_cost", "search_universities", "university_data_unavailable", None}

    print(f"[PASS] Prompt: {prompt}")
    print(
        "       university_mcp_used=",
        payload.get("mcp", {}).get("universityCost", {}).get("used"),
        "mode=",
        payload.get("mcp", {}).get("universityCost", {}).get("mode"),
        "graph_type=",
        payload.get("graph", {}).get("type"),
    )


def main() -> None:
    check_health()
    for prompt in PROMPTS:
        evaluate_prompt(prompt)

    print("\nAll integration evaluations passed.")


if __name__ == "__main__":
    main()
