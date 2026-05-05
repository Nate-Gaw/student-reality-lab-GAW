from __future__ import annotations

import json
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

import requests
from sqlalchemy import select
from flask import Blueprint, jsonify, request

from backend.api.graphs import build_graph_from_profiles
from backend.database.models import Alias, SessionLocal, University
from backend.services.rag_service import get_rag_snippets
from backend.services.roi_engine import rank_by_roi
from backend.services.university_resolver import resolve_universities, extract_candidates
from backend.services.university_service import get_university_profiles


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.2")
OPENAI_URL = os.getenv("OPENAI_URL", "https://api.openai.com/v1/chat/completions")

chat_bp = Blueprint("chat", __name__)
logger = logging.getLogger("college_roi.chat")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


def build_fallback_answer(profiles: List[Dict[str, Any]]) -> str:
    if not profiles:
        return (
            "I can give a baseline ROI comparison, but I need a specific university or program name "
            "to use verified cost and salary data."
        )

    ranked = rank_by_roi(profiles)
    top = ranked[0]
    roi = top["roi"]
    if len(ranked) == 1:
        return (
            f"Based on cached data, {top['university_name']} shows the strongest ROI. "
            f"Estimated total cost is ${roi['total_cost']:.0f}, median salary ${roi['median_salary']:.0f}, "
            f"and break-even is about {roi['break_even_years']} years."
        )

    comparisons = []
    for profile in ranked:
        roi = profile.get("roi", {})
        comparisons.append(
            f"{profile['university_name']}: total cost ${roi.get('total_cost', 0):.0f}, "
            f"median salary ${roi.get('median_salary', 0):.0f}, "
            f"break-even {roi.get('break_even_years', 0)} years"
        )

    return (
        "Based on cached data, here is a comparison: "
        + "; ".join(comparisons)
        + f". Strongest ROI: {top['university_name']}."
    )


def _detect_category(prompt: str) -> str | None:
    prompt_lower = prompt.lower()
    if any(keyword in prompt_lower for keyword in ["scholarship", "scholarships", "grant", "financial aid", "aid"]):
        return "scholarships"
    if any(keyword in prompt_lower for keyword in ["program", "curriculum", "track", "degree requirements"]):
        return "programs"
    return None


def _detect_query_type(prompt: str, resolved: List[str]) -> str:
    if resolved:
        if len(resolved) > 1:
            return "comparison"
        return "single"
    if prompt.strip().endswith("?"):
        return "general"
    return "general"


def _is_scholarship_query(prompt: str) -> bool:
    prompt_lower = prompt.lower()
    return "scholarship" in prompt_lower or "financial aid" in prompt_lower


def _filter_missing_candidates(candidates: List[str]) -> List[str]:
    if not candidates:
        return []

    with SessionLocal() as session:
        alias_rows = session.execute(select(Alias.alias)).all()
        name_rows = session.execute(select(University.name)).all()

    alias_set = {row[0].lower() for row in alias_rows}
    name_set = {row[0].lower() for row in name_rows}

    filtered = []
    for candidate in candidates:
        normalized = candidate.lower()
        if normalized in alias_set or normalized in name_set:
            filtered.append(candidate)
            continue
        if "university" in normalized or "college" in normalized:
            filtered.append(candidate)

    return filtered


def call_openai(prompt: str) -> str | None:
    if not OPENAI_API_KEY:
        return None

    try:
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
                        "content": (
                            "You are a concise college ROI advisor. Use ONLY provided context and do not output any numbers. "
                            "Do NOT invent or estimate any numeric values. Do NOT include digits or approximate language. "
                            "Return strict JSON with keys: summary, notes."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.4,
                "max_completion_tokens": 250,
            },
            timeout=(2, 2),
        )
    except requests.RequestException:
        return None

    if not response.ok:
        return None

    payload = response.json()
    choices = payload.get("choices", [])
    if choices:
        content = choices[0].get("message", {}).get("content", "")
        return content.strip() if content else None

    return None


def _build_db_payload(profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    db_rows = []
    for profile in profiles:
        roi = profile.get("roi", {})
        db_rows.append(
            {
                "university": profile.get("university_name"),
                "costs": profile.get("costs", {}),
                "salary": profile.get("salary", {}),
                "roi": roi,
            }
        )
    return db_rows


def _build_llm_db_context(profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    context_rows = []
    for profile in profiles:
        costs = profile.get("costs", {})
        salary = profile.get("salary", {})
        roi = profile.get("roi", {})
        context_rows.append(
            {
                "university": profile.get("university_name"),
                "costs_available": any(costs.get(key) for key in ["tuition", "housing", "living_cost", "application_fee"]),
                "salary_available": bool(salary.get("median_salary")),
                "roi_available": bool(roi.get("roi_10_year")),
            }
        )
    return context_rows


def build_prompt(user_prompt: str, universities: List[str], db_context: List[Dict[str, Any]], rag_snippets: List[dict]) -> str:
    final_prompt = {
        "query": user_prompt,
        "universities": universities,
        "db_data": db_context,
        "rag_data": rag_snippets,
    }
    logger.info("FINAL_PROMPT=%s", json.dumps(final_prompt, ensure_ascii=True))
    return json.dumps(final_prompt, ensure_ascii=True)


def _safe_llm_payload(text: str | None) -> Dict[str, str]:
    if not text:
        return {"summary": "", "notes": ""}
    forbidden = ["about", "around", "approx", "approximately", "~", "estimate", "estimated"]
    try:
        payload = json.loads(text)
        summary = str(payload.get("summary") or "").strip()
        notes = str(payload.get("notes") or "").strip()
        summary = re.sub(r"\d", "", summary)
        notes = re.sub(r"\d", "", notes)
        for word in forbidden:
            summary = re.sub(rf"\b{re.escape(word)}\b", "", summary, flags=re.IGNORECASE).strip()
            notes = re.sub(rf"\b{re.escape(word)}\b", "", notes, flags=re.IGNORECASE).strip()
        return {"summary": summary, "notes": notes}
    except json.JSONDecodeError:
        cleaned = re.sub(r"\d", "", text)
        for word in forbidden:
            cleaned = re.sub(rf"\b{re.escape(word)}\b", "", cleaned, flags=re.IGNORECASE).strip()
        return {"summary": cleaned.strip(), "notes": ""}


def _sanitize_rag_snippets(snippets: List[dict]) -> List[dict]:
    sanitized = []
    for snippet in snippets:
        text = re.sub(r"\d", "[NUM]", snippet.get("text", ""))
        sanitized.append(
            {
                "text": text,
                "university": snippet.get("university", ""),
                "category": snippet.get("category", ""),
            }
        )
    return sanitized


def _llm_output_is_safe(payload: Dict[str, str]) -> bool:
    combined = f"{payload.get('summary', '')} {payload.get('notes', '')}".lower()
    if re.search(r"\d", combined):
        return False
    forbidden = ["about", "around", "approx", "approximately", "~", "estimate", "estimated"]
    return not any(word in combined for word in forbidden)


def _db_payload_complete(profiles: List[Dict[str, Any]]) -> bool:
    if not profiles:
        return False
    for profile in profiles:
        costs = profile.get("costs", {})
        salary = profile.get("salary", {})
        required_costs = ["tuition", "housing", "living_cost", "application_fee"]
        if any(costs.get(key) is None for key in required_costs):
            return False
        if salary.get("median_salary") is None:
            return False
    return True


def _build_structured_response(
    profiles: List[Dict[str, Any]],
    llm_payload: Dict[str, str],
) -> Dict[str, Any]:
    universities = [profile["university_name"] for profile in profiles]
    cost_breakdown = {}
    roi_analysis = {}
    for profile in profiles:
        name = profile["university_name"]
        cost_breakdown[name] = profile.get("costs", {})
        roi_analysis[name] = profile.get("roi", {})

    return {
        "universities": universities,
        "summary": llm_payload.get("summary") or "",
        "cost_breakdown": cost_breakdown,
        "roi_analysis": roi_analysis,
        "notes": llm_payload.get("notes") or "",
    }


@chat_bp.post("/api/chat")
def chat() -> Any:
    body = request.get_json(silent=True) or {}
    user_prompt = (body.get("prompt") or "").strip()

    if not user_prompt:
        return jsonify({"error": "Missing prompt"}), 400

    candidates = extract_candidates(user_prompt)
    university_names = resolve_universities(user_prompt)
    if not university_names:
        hinted = extract_candidates(f"at {user_prompt}")
        if hinted:
            university_names = resolve_universities("compare " + " and ".join(hinted))

    category = _detect_category(user_prompt)
    is_scholarship = _is_scholarship_query(user_prompt)

    with ThreadPoolExecutor(max_workers=2) as executor:
        profiles_future = executor.submit(get_university_profiles, university_names)
        rag_future = executor.submit(get_rag_snippets, user_prompt, limit=3, universities=university_names, category=category)
        profiles = profiles_future.result()
        rag_snippets = rag_future.result()

    profiles = rank_by_roi(profiles) if profiles else []

    db_data = _build_db_payload(profiles)
    db_context = _build_llm_db_context(profiles)
    prompt = build_prompt(user_prompt, university_names, db_context, _sanitize_rag_snippets(rag_snippets))

    logger.info("RESOLVED_UNIVERSITIES=%s", university_names)
    logger.info("DB_PAYLOAD=%s", json.dumps(db_data, ensure_ascii=True))
    logger.info("RAG_CHUNKS=%s", json.dumps(rag_snippets, ensure_ascii=True))

    llm_payload = _safe_llm_payload(call_openai(prompt))
    structured = _build_structured_response(profiles, llm_payload)

    is_unknown = bool(candidates) and not profiles
    query_type = _detect_query_type(user_prompt, university_names)
    is_general = query_type == "general" and not is_unknown and not is_scholarship
    if is_unknown:
        structured = None
    elif is_general and structured:
        structured["notes"] = structured.get("notes") or "General advice mode"

    llm_safe = _llm_output_is_safe(llm_payload)
    db_complete = _db_payload_complete(profiles) if profiles else False
    validator_ok = (llm_safe and (db_complete or is_unknown or is_general or is_scholarship))

    if is_unknown:
        summary_text = "No verified data available for this institution."
    elif is_general:
        summary_text = structured.get("summary", "General advice mode.") if structured else "General advice mode."
    elif structured and structured["summary"]:
        summary_text = structured["summary"]
    elif candidates and not profiles:
        filtered_candidates = _filter_missing_candidates(candidates)
        if filtered_candidates:
            missing_list = ", ".join(filtered_candidates)
            summary_text = (
                "Verified data not available for the following schools in the database: "
                f"{missing_list}."
            )
        else:
            summary_text = "Verified data not available."
    else:
        summary_text = build_fallback_answer(profiles)

    if is_scholarship:
        answer = " ".join([snippet.get("text", "") for snippet in rag_snippets]).strip()
        if not answer:
            answer = "No verified scholarship information available."
        graph = None
    elif profiles:
        details = []
        for profile in profiles:
            roi = profile.get("roi", {})
            details.append(
                f"{profile['university_name']}: total cost ${roi.get('total_cost', 0):.0f}, "
                f"median salary ${roi.get('median_salary', 0):.0f}, "
                f"break-even {roi.get('break_even_years')} years"
            )
        answer = f"{summary_text}\nVerified data: " + "; ".join(details)
    else:
        answer = summary_text

    if not is_scholarship:
        graph = build_graph_from_profiles(profiles)

    response_payload = {
        "answer": answer,
        "structured": structured,
        "graph": graph,
        "metadata": {
            "resolved_candidates": university_names,
            "detected_candidates": candidates,
            "profile_count": len(profiles),
            "university_names": [p["university_name"] for p in profiles],
            "rag_used": bool(rag_snippets),
            "rag_category": category,
            "validator_ok": validator_ok,
        },
    }

    logger.info("FINAL_RESPONSE=%s", json.dumps(response_payload, ensure_ascii=True))

    if not validator_ok:
        safe_payload = {
            "answer": "No verified data available.",
            "structured": None,
            "graph": None,
            "metadata": {
                "resolved_candidates": university_names,
                "detected_candidates": candidates,
                "profile_count": len(profiles),
                "university_names": [p["university_name"] for p in profiles],
                "rag_used": bool(rag_snippets),
                "rag_category": category,
                "validator_ok": False,
            },
        }
        logger.info("FINAL_RESPONSE_REJECTED=%s", json.dumps(safe_payload, ensure_ascii=True))
        return jsonify(safe_payload), 422

    return jsonify(response_payload)
