from __future__ import annotations

import re
from typing import Iterable, List

from sqlalchemy import select

from backend.cache.redis_cache import cache
from backend.database.models import Alias, University, SessionLocal
from backend.utils.fuzzy_matching import best_match


CANDIDATE_PATTERN = re.compile(
    r"(?:at|to|for|from|of|vs|versus|compare|between)\s+([A-Za-z0-9\-&,\.\s]{3,80})",
    re.IGNORECASE,
)

TRAILING_STOPWORDS = {
    "is",
    "are",
    "was",
    "were",
    "do",
    "does",
    "did",
    "can",
    "could",
    "should",
    "would",
    "good",
    "worth",
    "it",
    "cs",
    "computer",
    "science",
    "master",
    "masters",
    "degree",
    "program",
    "roi",
}


def _clean_candidate(text: str) -> str:
    cleaned = text.strip(" .,;:")
    tokens = [t for t in re.split(r"\s+", cleaned) if t]
    while tokens and tokens[0].lower() in TRAILING_STOPWORDS:
        tokens.pop(0)
    while tokens and tokens[-1].lower() in TRAILING_STOPWORDS:
        tokens.pop()
    return " ".join(tokens).strip()


def extract_candidates(prompt: str) -> List[str]:
    if not prompt:
        return []

    candidates = set()
    for match in CANDIDATE_PATTERN.findall(prompt):
        cleaned = _clean_candidate(match)
        if len(cleaned) >= 3:
            parts = re.split(r"\s+(?:vs|versus|and)\s+|,", cleaned, flags=re.IGNORECASE)
            for part in parts:
                part = _clean_candidate(part)
                if len(part) >= 3:
                    candidates.add(part)

    title_case = re.findall(r"([A-Z][A-Za-z&\-]+(?:\s+[A-Z][A-Za-z&\-]+){0,4})", prompt)
    for name in title_case:
        cleaned = _clean_candidate(name)
        if len(cleaned) >= 3:
            candidates.add(cleaned)

    filtered = []
    for candidate in candidates:
        tokens = [t for t in candidate.split() if t]
        if len(tokens) == 1 and tokens[0].lower() in TRAILING_STOPWORDS:
            continue
        filtered.append(candidate)

    return sorted(filtered, key=len, reverse=True)


def _get_university_names() -> List[str]:
    with SessionLocal() as session:
        names = [row[0] for row in session.execute(select(University.name)).all()]
    return names


def _get_alias_map() -> dict[str, str]:
    with SessionLocal() as session:
        rows = session.execute(select(Alias.alias, University.name).join(University)).all()

    alias_map = {alias.lower(): name for alias, name in rows}
    return alias_map


def _token_overlap(a: str, b: str) -> float:
    tokens_a = {t for t in a.lower().split() if len(t) > 2}
    tokens_b = {t for t in b.lower().split() if len(t) > 2}
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / max(len(tokens_a), 1)


def resolve_universities(prompt: str) -> List[str]:
    candidates = extract_candidates(prompt)
    if not candidates:
        return []

    alias_map = _get_alias_map()
    university_names = _get_university_names()
    resolved = []

    for candidate in candidates:
        normalized = candidate.lower()

        if normalized in alias_map:
            resolved.append(alias_map[normalized])
            continue

        exact = next((name for name in university_names if name.lower() == normalized), None)
        if exact:
            resolved.append(exact)
            continue

        if "university" in normalized or "college" in normalized or len(normalized) >= 6:
            fuzzy = best_match(candidate, university_names, score_cutoff=92)
            if fuzzy and _token_overlap(candidate, fuzzy[0]) >= 0.5:
                resolved.append(fuzzy[0])

    unique = []
    seen = set()
    for name in resolved:
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        unique.append(name)

    return unique
