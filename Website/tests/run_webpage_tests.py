import json
import re
import time
from pathlib import Path

import requests

BASE = Path(__file__).resolve().parent
PROMPTS_PATH = BASE / "webpage_tests.json"
RESULTS_PATH = BASE / "webpage_test_results.json"
API_URL = "http://localhost:5056/api/chat"
TIMEOUT_SECONDS = 10

SCHOOL_ALIASES = {
    "njit": "New Jersey Institute of Technology",
    "rutgers": "Rutgers University-New Brunswick",
    "rutgers nb": "Rutgers University-New Brunswick",
    "stanford": "Stanford University",
    "mit": "Massachusetts Institute of Technology",
    "carnegie mellon": "Carnegie Mellon University",
    "cmu": "Carnegie Mellon University",
    "university of michigan": "University of Michigan",
    "uc berkeley": "University of California, Berkeley",
    "university of california, berkeley": "University of California, Berkeley",
    "berkeley": "University of California, Berkeley",
    "harvard": "Harvard University",
    "princeton": "Princeton University",
}

ANSWER_TERMS = {
    "New Jersey Institute of Technology": ["new jersey institute of technology", "njit"],
    "Rutgers University-New Brunswick": ["rutgers", "rutgers nb", "rutgers new brunswick"],
    "Stanford University": ["stanford"],
    "Massachusetts Institute of Technology": ["massachusetts institute of technology", "mit"],
    "Carnegie Mellon University": ["carnegie mellon", "cmu"],
    "University of Michigan": ["university of michigan", "u michigan", "umich"],
    "University of California, Berkeley": ["university of california, berkeley", "uc berkeley", "berkeley"],
    "Harvard University": ["harvard"],
    "Princeton University": ["princeton"],
}


def _extract_expected(prompt: str) -> list[str]:
    prompt_lower = prompt.lower()
    expected = set()
    for alias, canonical in sorted(SCHOOL_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if alias in prompt_lower:
            expected.add(canonical)
    return sorted(expected)


def _answer_mentions(answer: str, expected: list[str]) -> list[str]:
    if not answer:
        return []
    answer_lower = answer.lower()
    mentions = []
    for canonical in expected:
        terms = ANSWER_TERMS.get(canonical, [canonical.lower()])
        if any(term in answer_lower for term in terms):
            mentions.append(canonical)
    return mentions


def run() -> None:
    prompts = json.loads(PROMPTS_PATH.read_text(encoding="utf-8"))
    results = []
    forbidden_words = ["about", "around", "approx", "approximately", "~", "estimate", "estimated"]

    for i, prompt in enumerate(prompts, 1):
        start = time.time()
        try:
            response = requests.post(API_URL, json={"prompt": prompt}, timeout=TIMEOUT_SECONDS)
            elapsed = round(time.time() - start, 3)
            ok = response.status_code == 200
            payload = response.json() if ok else {"error": response.text}
            answer = payload.get("answer") if ok else None
            graph = payload.get("graph") if ok else None
            structured = payload.get("structured") if ok else None
            structured_keys = {"universities", "summary", "cost_breakdown", "roi_analysis", "notes"}
            structured_present = isinstance(structured, dict)
            structured_valid = structured_present and structured_keys.issubset(set(structured.keys()))
            expected_colleges = _extract_expected(prompt)
            resolved_candidates = payload.get("metadata", {}).get("resolved_candidates") if ok else None
            validator_ok = payload.get("metadata", {}).get("validator_ok") if ok else None
            resolved_set = {name.lower() for name in (resolved_candidates or [])}
            mentioned_in_answer = _answer_mentions(answer or "", expected_colleges)
            missing_in_answer = [name for name in expected_colleges if name not in mentioned_in_answer]
            missing_in_metadata = [name for name in expected_colleges if name.lower() not in resolved_set]
            structured_universities = structured.get("universities", []) if structured_present else []
            missing_in_structured = [name for name in expected_colleges if name not in structured_universities]
            expects_no_data = any(token in prompt.lower() for token in ["unknown", "gotham", "atlantis", "fake", "xyz"])
            summary_text = structured.get("summary", "") if structured_present else ""
            notes_text = structured.get("notes", "") if structured_present else ""
            verified_missing = expects_no_data and ("no verified data available" in (answer or "").lower())
            structured_null_expected = expects_no_data
            structured_is_null = structured is None
            llm_has_digits = bool(re.search(r"\d", f"{summary_text} {notes_text}")) if structured_present else False
            llm_has_estimates = any(word in f"{summary_text} {notes_text}".lower() for word in forbidden_words) if structured_present else False
            is_scholarship_query = "scholarship" in prompt.lower() or "financial aid" in prompt.lower()
            scholarship_routed = is_scholarship_query and (graph is None)
            expected_shell = (not expected_colleges) and not expects_no_data
            structured_shell_ok = expected_shell and structured_present and structured_valid
            rutgers_expected_total = 32000 + 14000 + 12000
            njit_expected_total = 28000 + 12000 + 11000
            totals_match = True
            if structured_present:
                if "Rutgers University-New Brunswick" in structured.get("roi_analysis", {}):
                    totals_match &= structured["roi_analysis"]["Rutgers University-New Brunswick"].get("total_cost") == rutgers_expected_total
                if "New Jersey Institute of Technology" in structured.get("roi_analysis", {}):
                    totals_match &= structured["roi_analysis"]["New Jersey Institute of Technology"].get("total_cost") == njit_expected_total
            results.append(
                {
                    "i": i,
                    "prompt": prompt,
                    "status": response.status_code,
                    "elapsed_s": elapsed,
                    "answer_present": bool(answer),
                    "graph_type": graph.get("type") if isinstance(graph, dict) else None,
                    "profile_count": payload.get("metadata", {}).get("profile_count") if ok else None,
                    "resolved_candidates": resolved_candidates,
                    "expected_colleges": expected_colleges,
                    "answer_mentions": mentioned_in_answer,
                    "missing_in_answer": missing_in_answer,
                    "missing_in_metadata": missing_in_metadata,
                    "structured_present": structured_present,
                    "structured_valid": structured_valid,
                    "missing_in_structured": missing_in_structured,
                    "verified_missing": verified_missing,
                    "structured_is_null": structured_is_null,
                    "structured_null_expected": structured_null_expected,
                    "llm_has_digits": llm_has_digits,
                    "llm_has_estimates": llm_has_estimates,
                    "scholarship_routed": scholarship_routed,
                    "structured_shell_ok": structured_shell_ok,
                    "totals_match": totals_match,
                    "validator_ok": validator_ok,
                    "answer": answer,
                    "error": payload.get("error") if not ok else None,
                }
            )
        except Exception as exc:
            elapsed = round(time.time() - start, 3)
            results.append(
                {
                    "i": i,
                    "prompt": prompt,
                    "status": "error",
                    "elapsed_s": elapsed,
                    "answer_present": False,
                    "graph_type": None,
                    "profile_count": None,
                    "resolved_candidates": None,
                    "expected_colleges": _extract_expected(prompt),
                    "answer_mentions": [],
                    "missing_in_answer": [],
                    "missing_in_metadata": [],
                    "structured_present": False,
                    "structured_valid": False,
                    "missing_in_structured": [],
                    "verified_missing": False,
                    "answer": None,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

        RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"{i:02d} | {results[-1]['status']} | {results[-1]['elapsed_s']}s | {results[-1]['graph_type']}")

    print("\nSaved:", RESULTS_PATH)


if __name__ == "__main__":
    run()
