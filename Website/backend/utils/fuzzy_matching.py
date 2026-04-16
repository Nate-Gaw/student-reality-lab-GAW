from __future__ import annotations

from typing import Iterable, Optional, Tuple

from rapidfuzz import process


def best_match(query: str, candidates: Iterable[str], score_cutoff: int = 85) -> Optional[Tuple[str, float]]:
    if not query:
        return None

    match = process.extractOne(query, list(candidates), score_cutoff=score_cutoff)
    if not match:
        return None

    name, score, _ = match
    return name, float(score)
