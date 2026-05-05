from __future__ import annotations

import json
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from backend.api.chat import (
    _build_db_payload,
    _build_llm_db_context,
    _build_structured_response,
    _db_payload_complete,
    _detect_category,
    _detect_query_type,
    _filter_missing_candidates,
    _is_scholarship_query,
    _llm_output_is_safe,
    _safe_llm_payload,
    _sanitize_rag_snippets,
    build_fallback_answer,
    build_prompt,
    call_openai,
)
from backend.api.graphs import build_graph_from_profiles
from backend.database.models import Alias, Base, SessionLocal, University, engine
from backend.services.rag_service import get_rag_snippets
from backend.services.roi_engine import attach_roi, rank_by_roi
from backend.services.university_resolver import extract_candidates, resolve_universities
from backend.services.university_service import get_university_profiles


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

logger = logging.getLogger("college_roi.api")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

app = FastAPI(title="college-roi-advisor")


def _read_frontend_dir() -> Path:
    return PROJECT_ROOT / "frontend" / "dist"


@app.on_event("startup")
def _startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "service": "college-roi-advisor"}


@app.post("/api/chat")
async def chat(request: Request) -> JSONResponse:
    body = await request.json() if request.headers.get("content-type") else {}
    user_prompt = str((body or {}).get("prompt") or "").strip()

    if not user_prompt:
        return JSONResponse(status_code=400, content={"error": "Missing prompt"})

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
    validator_ok = llm_safe and (db_complete or is_unknown or is_general or is_scholarship)

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
        return JSONResponse(status_code=422, content=safe_payload)

    return JSONResponse(content=response_payload)


@app.post("/api/graphs")
async def graphs(request: Request) -> JSONResponse:
    body = await request.json() if request.headers.get("content-type") else {}
    names = list((body or {}).get("universities", []))
    if not names:
        return JSONResponse(status_code=400, content={"error": "Missing universities"})

    profiles = attach_roi(get_university_profiles(names))
    graph = build_graph_from_profiles(profiles)
    return JSONResponse(content={"graph": graph})


@app.get("/debug")
def debug() -> Dict[str, Any]:
    return {"frontend_path": str(_read_frontend_dir())}


app.mount("/", StaticFiles(directory=str(_read_frontend_dir()), html=True), name="frontend")
