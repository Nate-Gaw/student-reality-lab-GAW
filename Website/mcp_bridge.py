"""Local bridge API that integrates Website chat with University Cost MCP and Graph Generation MCP."""

from __future__ import annotations

import json
import os
import re
import sys
import importlib.util
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
UNIVERSITY_MCP_ROOT = PROJECT_ROOT / "university-cost-mcp"
GRAPH_MCP_ROOT = PROJECT_ROOT / "graph-generation-mcp"

# Load shared root-level environment variables once for bridge + MCP modules.
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# Make MCP project modules importable.
if str(UNIVERSITY_MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(UNIVERSITY_MCP_ROOT))
if str(GRAPH_MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(GRAPH_MCP_ROOT))

from data.storage.database import DatabaseManager  # type: ignore  # noqa: E402


def _load_module(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module spec for {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_query_handler_module = _load_module(
    "university_cost_query_handler",
    UNIVERSITY_MCP_ROOT / "server" / "query_handler.py",
)
_graph_generator_module = _load_module(
    "graph_generation_graph_generator",
    GRAPH_MCP_ROOT / "server" / "graph_generator.py",
)

QueryHandler = _query_handler_module.QueryHandler
GraphGenerator = _graph_generator_module.GraphGenerator

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

BASELINE_SCENARIO: Dict[str, float] = {
    "bachelorDebt": 27437,
    "masterDebt": 61667,
    "repaymentYears": 10,
    "interestRate": 5,
    "bachelorSalary": 85500,
    "masterSalary": 95400,
    "growthRate": 3,
    "taxRate": 24,
    "costIndex": 1,
}

app = Flask(__name__)
CORS(app)


def calculate_monthly_payment(principal: float, annual_rate: float, years_to_repay: int) -> float:
    if principal <= 0 or years_to_repay <= 0:
        return 0

    monthly_rate = annual_rate / 100 / 12
    num_payments = years_to_repay * 12

    if monthly_rate == 0:
        return principal / num_payments

    numerator = monthly_rate * (1 + monthly_rate) ** num_payments
    denominator = (1 + monthly_rate) ** num_payments - 1
    return principal * (numerator / denominator)


def project_earnings(
    start_salary: float,
    growth_rate: float,
    years_to_project: int = 30,
    total_debt: float = 0,
    annual_rate: float = 5,
    repayment_years: int = 10,
    tax_rate: float = 0,
    cost_index: float = 1,
) -> List[Dict[str, int]]:
    projection: List[Dict[str, int]] = []
    current_salary = start_salary
    cumulative_earnings = 0.0

    monthly_payment = calculate_monthly_payment(total_debt, annual_rate, repayment_years)
    annual_payment = monthly_payment * 12

    for year in range(0, years_to_project + 1):
        if year > 0:
            current_salary *= 1 + growth_rate / 100

        is_repaying_debt = year > 0 and year <= repayment_years
        payment_this_year = annual_payment if is_repaying_debt else 0

        tax_amount = current_salary * (tax_rate / 100)
        after_tax_income = current_salary - tax_amount
        cost_adjusted_income = after_tax_income / cost_index if cost_index > 0 else after_tax_income
        net_earnings_this_year = cost_adjusted_income - payment_this_year

        cumulative_earnings += net_earnings_this_year

        projection.append(
            {
                "year": year,
                "netEarningsThisYear": round(net_earnings_this_year),
                "cumulativeNet": round(cumulative_earnings),
            }
        )

    return projection


def compute_break_even_year(
    bachelor_projection: List[Dict[str, int]],
    master_projection: List[Dict[str, int]],
) -> Optional[int]:
    years = min(len(bachelor_projection), len(master_projection))
    for i in range(years):
        if master_projection[i]["cumulativeNet"] >= bachelor_projection[i]["cumulativeNet"]:
            return i
    return None


def build_financial_summary(scenario: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    active = scenario or BASELINE_SCENARIO

    bachelor_projection = project_earnings(
        start_salary=active["bachelorSalary"],
        growth_rate=active["growthRate"],
        total_debt=active["bachelorDebt"],
        annual_rate=active["interestRate"],
        repayment_years=int(active["repaymentYears"]),
        tax_rate=active["taxRate"],
        cost_index=active["costIndex"],
    )

    master_projection = project_earnings(
        start_salary=active["masterSalary"],
        growth_rate=active["growthRate"],
        total_debt=active["masterDebt"],
        annual_rate=active["interestRate"],
        repayment_years=int(active["repaymentYears"]),
        tax_rate=active["taxRate"],
        cost_index=active["costIndex"],
    )

    break_even_year = compute_break_even_year(bachelor_projection, master_projection)

    return {
        "scenario": active,
        "breakEvenYear": break_even_year,
        "bachelorProjection": bachelor_projection,
        "masterProjection": master_projection,
        "bachelorMonthly": round(
            calculate_monthly_payment(active["bachelorDebt"], active["interestRate"], int(active["repaymentYears"]))
        ),
        "masterMonthly": round(
            calculate_monthly_payment(active["masterDebt"], active["interestRate"], int(active["repaymentYears"]))
        ),
        "bachelorTotal30": bachelor_projection[30]["cumulativeNet"],
        "masterTotal30": master_projection[30]["cumulativeNet"],
        "advantage15": master_projection[15]["cumulativeNet"] - bachelor_projection[15]["cumulativeNet"],
        "advantage30": master_projection[30]["cumulativeNet"] - bachelor_projection[30]["cumulativeNet"],
    }


def ensure_university_sample_data(db: DatabaseManager) -> None:
    """Load sample university data, updating database with any new or changed entries."""
    db.create_tables()

    sample_file = UNIVERSITY_MCP_ROOT / "sample_data" / "universities.json"
    if not sample_file.exists():
        return

    with sample_file.open("r", encoding="utf-8") as handle:
        universities = json.load(handle)

    # For each university in sample data, add or update it in the database
    for uni in universities:
        uni["last_updated"] = datetime.now()
        costs = [
            uni.get("international_tuition", 0),
            uni.get("estimated_housing_cost", 0),
            uni.get("estimated_living_cost", 0),
            uni.get("student_fees", 0),
            uni.get("books_supplies", 0),
            uni.get("health_insurance", 0),
        ]
        uni["estimated_total_annual_cost"] = sum(float(c) for c in costs if c)
        
        try:
            # Always add - the database will handle duplicates by updating
            db.add_university(uni)
            print(f"Ensured in database: {uni.get('university_name')} ({uni.get('degree_level')})")
        except Exception as e:
            print(f"Could not add {uni.get('university_name')}: {e}")
            continue


def build_projection_graph(graph_generator: GraphGenerator, summary: Dict[str, Any]) -> Dict[str, Any]:
    data = []
    for year in range(0, 31):
        data.append(
            {
                "year": year,
                "bachelor_cumulative": summary["bachelorProjection"][year]["cumulativeNet"],
                "master_cumulative": summary["masterProjection"][year]["cumulativeNet"],
            }
        )

    graph = graph_generator.generate_comparison_chart(
        data=data,
        category_column="year",
        value_columns=["bachelor_cumulative", "master_cumulative"],
        title="30-Year Cumulative Net Earnings Projection",
    )

    return {
        "graph_type": graph.get("type", "comparison"),
        "title": "30-Year Cumulative Net Earnings Projection",
        "html": graph.get("html", ""),
        "metadata": graph.get("metadata", {}),
        "mcp_source": "graph-generation-mcp",
    }


def _normalize_for_prompt(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2)


def _load_university_names(handler: QueryHandler) -> List[str]:
    records = handler.db.search_universities("", limit=500)
    names = []
    seen = set()
    for row in records:
        name = row.get("university_name")
        if isinstance(name, str):
            key = name.lower().strip()
            if key and key not in seen:
                seen.add(key)
                names.append(name)
    return names


def _extract_university_candidate(user_prompt: str) -> Optional[str]:
    text = user_prompt.strip()
    patterns = [
        r"(?:at|to|for)\s+([A-Za-z0-9\-&,\.\s]{4,80}?)(?:\s+for\s+a|\?|\.|,|$)",
        r"(?:university|college)\s+of\s+([A-Za-z0-9\-&,\.\s]{2,60})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            candidate = match.group(1).strip(" .,")
            candidate = re.sub(r"^(go\s+to|apply\s+to|attend)\s+", "", candidate, flags=re.IGNORECASE)
            if len(candidate) >= 4:
                return candidate

    # Last-resort heuristic: title-cased chunks likely representing institution names.
    caps = re.findall(r"([A-Z][A-Za-z&\-]+(?:\s+[A-Z][A-Za-z&\-]+){0,5})", text)
    if caps:
        longest = sorted(caps, key=len, reverse=True)[0].strip()
        if len(longest) >= 6:
            return longest

    return None


def _extract_all_university_candidates(user_prompt: str) -> List[str]:
    """Extract ALL university mentions from user query, not just one."""
    text = user_prompt.strip()
    candidates = set()
    
    # Pattern 1: "at/to/for University X"
    pattern1_matches = re.findall(r"(?:at|to|for|from|of)\s+([A-Za-z0-9\-&,\.\s]{4,80}?)(?:\s+(?:for|and|vs|versus|or)|\?|\.|,|$)", text, re.IGNORECASE)
    for match in pattern1_matches:
        candidate = match.strip(" .,")
        candidate = re.sub(r"^(go\s+to|apply\s+to|attend)\s+", "", candidate, flags=re.IGNORECASE)
        if len(candidate) >= 4 and candidate.lower() not in ["a master", "a bachelor", "a degree"]:
            candidates.add(candidate)
    
    # Pattern 2: "University of X" or "College of X"
    pattern2_matches = re.findall(r"(?:university|college)\s+of\s+([A-Za-z0-9\-&,\.\s]{2,60})", text, re.IGNORECASE)
    for match in pattern2_matches:
        candidate = match.strip(" .,")
        if len(candidate) >= 2:
            candidates.add(candidate)
    
    # Pattern 3: Title-cased institution names
    caps = re.findall(r"([A-Z][A-Za-z&\-]+(?:\s+[A-Z][A-Za-z&\-]+){0,5})", text)
    for cap in caps:
        cap = cap.strip()
        if len(cap) >= 4 and cap.lower() not in ["the", "a", "is", "for", "and", "or", "but"]:
            candidates.add(cap)
    
    # Split comma-separated universities
    expanded = set()
    for candidate in candidates:
        if " and " in candidate.lower() or ", " in candidate:
            parts = re.split(r"\s+(?:and|,)\s+", candidate, flags=re.IGNORECASE)
            for part in parts:
                part = part.strip()
                if len(part) >= 4:
                    expanded.add(part)
        else:
            expanded.add(candidate)
    
    return sorted(list(expanded), key=len, reverse=True)


def _get_cost_for_candidate(handler: QueryHandler, candidate: str, degree: str = "master") -> Optional[Dict]:
    """Try to get cost data for a single candidate using exact match + fuzzy matching."""
    if not candidate:
        return None
    
    # Try exact match first
    results = handler.get_university_cost(candidate, degree, "international")
    
    # If got data or explicit error, return it
    if isinstance(results, dict) and "error" not in results:
        return results
    
    # If no exact match and error result, fuzzy matching already applied in query_handler
    # Just return the result (which might be error)
    if isinstance(results, dict) and "error" in results:
        return None  # Data not found
    
    return None


def get_university_context(handler: QueryHandler, user_prompt: str) -> Dict[str, Any]:
    prompt_lower = user_prompt.lower()
    names = _load_university_names(handler)

    # First try exact matches for known universities
    matched = [name for name in names if name.lower() in prompt_lower]
    matched = matched[:4]

    if len(matched) >= 2:
        print(f"\n[University MCP] Exact match found for {len(matched)} universities: {matched}")
        comparison = handler.compare_university_costs(matched, "master", "international")
        print(f"[University MCP] Comparison result: {comparison.get('count', 0)} universities in payload")
        return {
            "used": True,
            "mode": "compare_university_costs",
            "payload": comparison,
        }

    if len(matched) == 1:
        print(f"\n[University MCP] Exact match found: {matched[0]}")
        single = handler.get_university_cost(matched[0], "master", "international")
        return {
            "used": True,
            "mode": "get_university_cost",
            "payload": single,
        }

    # No exact matches found - try extracting ALL mentioned universities
    if re.search(r"\b(university|college|tuition|cost|debt|country|compare|vs|versus|roi|masters?|graduate|program)\b", prompt_lower):
        print(f"\n[University MCP] University-related query detected")
        candidates = _extract_all_university_candidates(user_prompt)
        print(f"[University MCP] Extracted candidates: {candidates}")
        
        successful_costs = []
        detected_but_unavailable = []
        
        # Try to get cost data for each candidate
        for candidate in candidates:
            cost_data = _get_cost_for_candidate(handler, candidate, "master")
            
            if cost_data:
                print(f"[University MCP] Found data for: {candidate}")
                successful_costs.append(cost_data)
            else:
                print(f"[University MCP] No data found for: {candidate}")
                detected_but_unavailable.append(candidate)
        
        # If we got multiple universities with data, do comparison
        if len(successful_costs) >= 2:
            print(f"[University MCP] Multiple universities found, creating comparison")
            # Create comparison payload from individual results
            universities_list = [cost["university_name"] for cost in successful_costs]
            comparison = handler.compare_university_costs(universities_list, "master", "international")
            print(f"[University MCP] Comparison result: {comparison.get('count', 0)} universities")
            return {
                "used": True,
                "mode": "compare_university_costs",
                "payload": comparison,
            }
        
        # If we got one university with data, return it
        if len(successful_costs) == 1:
            print(f"[University MCP] Single university found: {successful_costs[0].get('university_name')}")
            return {
                "used": True,
                "mode": "get_university_cost",
                "payload": successful_costs[0],
            }
        
        # If we detected universities but none have data, be specific about what was detected
        if detected_but_unavailable:
            print(f"[University MCP] Universities detected but data unavailable: {detected_but_unavailable}")
            return {
                "used": True,
                "mode": "university_detected_unavailable",
                "payload": {
                    "detected_universities": detected_but_unavailable,
                    "note": f"Detected query about {', '.join(detected_but_unavailable)}, but detailed cost data is not currently available.",
                },
            }
        
        # Last resort: try single candidate extraction for backward compatibility
        candidate = _extract_university_candidate(user_prompt)
        if candidate:
            print(f"[University MCP] Fallback candidate: {candidate}")
            direct = handler.get_university_cost(candidate, "master", "international")
            if isinstance(direct, dict) and "error" not in direct:
                return {
                    "used": True,
                    "mode": "get_university_cost",
                    "payload": direct,
                }
            elif isinstance(direct, dict) and "error" in direct:
                return {
                    "used": True,
                    "mode": "university_detected_unavailable",
                    "payload": {
                        "detected_university": candidate,
                        "note": f"Detected query about {candidate}, but detailed cost data is not currently available.",
                    },
                }

        search_term = candidate or user_prompt
        search = handler.search_universities(search_term, limit=5)

        if isinstance(search, dict) and search.get("count", 0) == 0 and candidate:
            # Try token-only fallback if the first phrase still failed.
            token_fallback = re.sub(r"[^a-zA-Z0-9\s]", " ", candidate)
            token_fallback = " ".join(token_fallback.split())
            if token_fallback and token_fallback != search_term:
                search = handler.search_universities(token_fallback, limit=5)

        if isinstance(search, dict) and search.get("count", 0) > 0:
            return {
                "used": True,
                "mode": "search_universities",
                "payload": search,
            }

        # If we detected a candidate but no results, acknowledge it
        if candidate:
            return {
                "used": True,
                "mode": "university_detected_unavailable",
                "payload": {
                    "detected_university": candidate,
                    "note": f"Detected query about {candidate}, but this university is not in our database.",
                },
            }

        # University MCP is supplemental: if no usable result, continue without surfacing a hard error path.
        return {
            "used": False,
            "mode": "university_data_unavailable",
            "payload": None,
        }

    return {"used": False, "mode": None, "payload": None}


def maybe_build_cost_graph(
    graph_generator: GraphGenerator,
    university_context: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    if not university_context.get("used"):
        return None

    payload = university_context.get("payload")

    if university_context.get("mode") == "compare_university_costs":
        universities = payload.get("universities", []) if isinstance(payload, dict) else []
        rows = []
        for uni in universities:
            costs = uni.get("costs", {})
            rows.append(
                {
                    "university": uni.get("university_name", "Unknown"),
                    "tuition": costs.get("tuition") or 0,
                    "total_annual_cost": uni.get("estimated_total_annual_cost") or 0,
                }
            )

        if len(rows) >= 2:
            graph = graph_generator.generate_comparison_chart(
                data=rows,
                category_column="university",
                value_columns=["tuition", "total_annual_cost"],
                title="University Cost Comparison (MCP Data)",
            )
            return {
                "graph_type": graph.get("type", "comparison"),
                "title": "University Cost Comparison (MCP Data)",
                "html": graph.get("html", ""),
                "metadata": graph.get("metadata", {}),
                "mcp_source": "graph-generation-mcp",
            }

    if university_context.get("mode") == "get_university_cost":
        if not isinstance(payload, dict) or payload.get("error"):
            return None

        costs = payload.get("costs", {}) if isinstance(payload, dict) else {}

        row = []
        for label, key in [
            ("Tuition", "tuition"),
            ("Housing", "housing"),
            ("Living", "living_expenses"),
            ("Fees", "student_fees"),
            ("Books", "books_supplies"),
        ]:
            raw = costs.get(key, 0)
            try:
                amount = float(raw or 0)
            except (TypeError, ValueError):
                amount = 0.0
            row.append({"category": label, "amount": amount})

        # Pie charts become effectively blank when all slices are zero.
        if not any(item["amount"] > 0 for item in row):
            return None

        graph = graph_generator.generate_graph(
            data=row,
            x_column="category",
            y_column="amount",
            graph_type="pie",
            title=f"{payload.get('university_name', 'University')} Cost Breakdown",
        )
        return {
            "graph_type": graph.get("type", "pie"),
            "title": f"{payload.get('university_name', 'University')} Cost Breakdown",
            "html": graph.get("html", ""),
            "metadata": graph.get("metadata", {}),
            "mcp_source": "graph-generation-mcp",
        }

    return None


def build_system_prompt(
    summary: Dict[str, Any],
    university_context: Dict[str, Any],
    graph_info: Optional[Dict[str, Any]],
) -> str:
    lines = [
        "You are a decision advisor for CS Master's ROI.",
        "You are integrated with two MCP tools:",
        "1) university-cost-mcp for retrieving real cost/university data (data retrieval ONLY).",
        "2) graph-generation-mcp for projections and cost visualizations.",
        "",
        "IMPORTANT: Provide your final answer directly. Do NOT show your thinking process or intermediate steps.",
        "Do NOT say 'I will fetch', 'let me retrieve', or 'first I need to'. Simply provide the analysis.",
        "",
        "IMPORTANT MCP USAGE:",
        "- The University Cost MCP is ONLY used to retrieve raw university cost data.",
        "- YOU are responsible for comparison, analysis, ranking, and ROI calculations.",
        "- When multiple universities are provided, compare them, rank them by ROI, and analyze the differences.",
        "- Use the MCP data as authoritative source values, then perform the analysis and recommendation yourself.",
        "",
    ]
    
    # Handle different data availability scenarios
    mode = university_context.get("mode")
    if mode == "university_detected_unavailable":
        lines.extend([
            "IMPORTANT: Specific universities were detected in the query, but detailed cost data is NOT available.",
            "DO NOT use baseline financial projections as if they represent these universities.",
            "Be honest that the data for these universities is not currently available.",
            "Suggest the user: Check the universities' official websites, contact admissions, or use resource aggregators.",
            "",
        ])
    elif mode in ["get_university_cost", "compare_university_costs"]:
        lines.extend([
            "Real university cost data is available from the University Cost MCP.",
            "Use this data to perform detailed comparisons, ROI analysis, and recommendations.",
            "",
        ])
    
    lines.extend([
        "Response structure:",
        "1) Direct answer based on available data (or honest acknowledgment of data gaps)",
        "2) Detailed comparison if multiple universities provided",
        "3) ROI analysis using the financial model + MCP data",
        "4) Risk caveats",
        "5) One clear action step",
        "",
    ])
    
    # Only include financial model if no specific university was queried or if real data available
    if mode != "university_detected_unavailable":
        lines.extend([
            "Baseline financial model (for general comparison when real data unavailable):",
            f"- Break-even year: {summary['breakEvenYear'] if summary['breakEvenYear'] is not None else 'No break-even in 30 years'}",
            f"- Bachelor monthly loan: {summary['bachelorMonthly']}",
            f"- Master monthly loan: {summary['masterMonthly']}",
            f"- Bachelor 30-year net: {summary['bachelorTotal30']}",
            f"- Master 30-year net: {summary['masterTotal30']}",
            f"- 15-year advantage (Master-Bachelor): {summary['advantage15']}",
            f"- 30-year advantage (Master-Bachelor): {summary['advantage30']}",
            "",
        ])
    
    lines.extend([
        "University Cost MCP data:",
        _normalize_for_prompt(university_context if university_context.get("used") else {"used": False}),
    ])
    
    if graph_info:
        lines.extend([
            "",
            "Available visualizations:",
            _normalize_for_prompt({k: v for k, v in graph_info.items() if k != "html"}),
        ])
    else:
        lines.extend([
            "",
            "Visualizations: None available (insufficient data for the requested universities)",
        ])
    
    return "\n".join(lines)


def call_openai(system_prompt: str, user_prompt: str) -> str:
    if not OPENAI_API_KEY:
        return (
            "MCP evaluation mode is active (OPENAI_API_KEY not set). "
            "I used University Cost MCP and Graph MCP contexts to prepare this response path. "
            "Set OPENAI_API_KEY to enable full natural-language advisor output."
        )

    try:
        # Log what we're sending (first 500 chars of system prompt for debugging)
        print(f"\n[OpenAI Call] Model: {OPENAI_MODEL}")
        print(f"[OpenAI Call] System prompt (first 300 chars): {system_prompt[:300]}...")
        print(f"[OpenAI Call] User prompt: {user_prompt}")
        
        response = requests.post(
            OPENAI_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}",
            },
            json={
                "model": OPENAI_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                "temperature": 0.7,
                "max_tokens": 2000,
            },
            timeout=45,
        )
    except Exception as exc:
        print(f"[OpenAI Call] Network error: {exc}")
        return (
            "Unable to reach OpenAI right now, but MCP data and graph generation are available. "
            f"Network detail: {exc}"
        )

    if not response.ok:
        error_text = response.text
        print(f"[OpenAI Call] Error {response.status_code}: {error_text}")
        raise RuntimeError(f"OpenAI error {response.status_code}: {error_text}")

    payload = response.json()
    print(f"[OpenAI Call] Response received, status ok")

    # Extract answer from standard OpenAI Chat Completion response
    try:
        choices = payload.get("choices", [])
        if choices and len(choices) > 0:
            message = choices[0].get("message", {})
            content = message.get("content", "").strip()
            if content:
                print(f"[OpenAI Call] Answer (first 200 chars): {content[:200]}...")
                return content
    except (KeyError, IndexError, AttributeError) as e:
        print(f"[OpenAI Call] Error parsing response: {e}")

    print(f"[OpenAI Call] Failed to extract content from: {payload}")
    raise RuntimeError(f"OpenAI returned unexpected response format: {payload}")


def build_services() -> Tuple[QueryHandler, GraphGenerator]:
    db_url = f"sqlite:///{(UNIVERSITY_MCP_ROOT / 'universities.db').as_posix()}"
    db = DatabaseManager(database_url=db_url)
    ensure_university_sample_data(db)
    return QueryHandler(db), GraphGenerator()


query_handler, graph_generator = build_services()


@app.get("/api/health")
def health() -> Any:
    return jsonify({"ok": True, "service": "website-mcp-bridge"})


@app.post("/api/advisor")
def advisor() -> Any:
    body = request.get_json(silent=True) or {}
    user_prompt = (body.get("prompt") or "").strip()

    if not user_prompt:
        return jsonify({"error": "Missing prompt"}), 400

    print(f"\n{'='*70}")
    print(f"[Advisor] Processing prompt: {user_prompt}")
    print(f"{'='*70}")

    summary = build_financial_summary()
    university_context = get_university_context(query_handler, user_prompt)
    
    print(f"[Advisor] University context mode: {university_context.get('mode')}")
    print(f"[Advisor] University context used: {university_context.get('used')}")

    # DO NOT generate graphs when no real university data is available
    # Only generate graphs when we have actual university data
    graph_info = None
    if university_context.get("mode") in ["get_university_cost", "compare_university_costs"]:
        # Real university data is available - generate cost graph
        cost_graph = maybe_build_cost_graph(graph_generator, university_context)
        if cost_graph:
            graph_info = cost_graph
            print(f"[Advisor] Generated cost graph: {cost_graph.get('title')}")
    elif not university_context.get("used"):
        # No university query detected at all - use baseline projection graph
        projection_graph = build_projection_graph(graph_generator, summary)
        graph_info = projection_graph
        print(f"[Advisor] Generated projection graph")
    else:
        print(f"[Advisor] No graph generated (data unavailable)")
    # else: university_detected_unavailable - NO GRAPH, NO FAKE DATA

    try:
        system_prompt = build_system_prompt(summary, university_context, graph_info)
        print(f"\n[Advisor] Calling OpenAI...")
        answer = call_openai(system_prompt, user_prompt)
        print(f"[Advisor] OpenAI response received ({len(answer)} chars)")
    except Exception as exc:
        print(f"[Advisor] Error: {exc}")
        return jsonify({"error": f"Advisor processing failed: {exc}"}), 500

    response_data = {
        "answer": answer,
        "summary": {
            "breakEvenYear": summary["breakEvenYear"],
            "advantage15": summary["advantage15"],
            "advantage30": summary["advantage30"],
        },
        "mcp": {
            "universityCost": {
                "used": university_context.get("used", False),
                "mode": university_context.get("mode"),
            },
        },
        "universityData": university_context.get("payload") if university_context.get("used") else None,
    }

    # Only include graph data if we actually have a graph
    if graph_info:
        response_data["mcp"]["graph"] = {
            "used": True,
            "type": graph_info.get("graph_type"),
            "title": graph_info.get("title"),
            "source": graph_info.get("mcp_source"),
        }
        response_data["graph"] = {
            "title": graph_info.get("title"),
            "type": graph_info.get("graph_type"),
            "html": graph_info.get("html"),
        }
    else:
        response_data["mcp"]["graph"] = {"used": False}
        response_data["graph"] = None

    print(f"[Advisor] Response ready, returning to client")
    return jsonify(response_data)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5055, debug=True)
