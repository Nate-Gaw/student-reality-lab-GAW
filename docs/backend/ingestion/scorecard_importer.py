from __future__ import annotations

import csv
import os
from datetime import datetime
from typing import Dict, Iterable

import requests
from dotenv import load_dotenv
from sqlalchemy import select

from backend.database.models import SalaryData, SessionLocal, TuitionCost, University


load_dotenv()
API_KEY = os.getenv("COLLEGE_SCORECARD_API_KEY")
BASE_URL = "https://api.data.gov/ed/collegescorecard/v1/schools"
COST_OF_LIVING_PATH = os.getenv("COST_OF_LIVING_PATH")

FIELDS = [
    "school.name",
    "school.city",
    "school.state",
    "latest.cost.tuition.in_state",
    "latest.cost.tuition.out_of_state",
    "latest.cost.roomboard.oncampus",
    "latest.cost.otherexpense.oncampus",
    "latest.admissions.application_fee",
    "latest.earnings.10_yrs_after_entry.median",
    "latest.debt.median_grad",
]


def _fetch_page(page: int = 0, per_page: int = 100) -> Dict:
    if not API_KEY:
        raise RuntimeError("COLLEGE_SCORECARD_API_KEY is required")

    params = {
        "api_key": API_KEY,
        "fields": ",".join(FIELDS),
        "per_page": per_page,
        "page": page,
    }

    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def _iter_records() -> Iterable[Dict]:
    page = 0
    while True:
        payload = _fetch_page(page=page)
        results = payload.get("results", [])
        if not results:
            break
        for record in results:
            yield record
        if page >= payload.get("metadata", {}).get("total_pages", 0) - 1:
            break
        page += 1


def _load_cost_of_living() -> Dict[str, float]:
    if not COST_OF_LIVING_PATH:
        return {}

    lookup: Dict[str, float] = {}
    try:
        with open(COST_OF_LIVING_PATH, "r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                city = (row.get("city") or "").strip()
                country = (row.get("country") or "").strip()
                cost = row.get("cost_of_living") or row.get("cost_of_living_index")
                if not city or not country or not cost:
                    continue
                key = f"{city.lower()}|{country.lower()}"
                try:
                    lookup[key] = float(cost)
                except ValueError:
                    continue
    except FileNotFoundError:
        return {}

    return lookup


def import_scorecard() -> None:
    now = datetime.utcnow().strftime("%Y-%m-%d")
    cost_of_living = _load_cost_of_living()
    with SessionLocal() as session:
        for record in _iter_records():
            name = record.get("school.name")
            if not name:
                continue

            university = session.scalar(select(University).where(University.name == name))
            if not university:
                university = University(
                    name=name,
                    city=record.get("school.city", ""),
                    country="USA",
                )
                session.add(university)
                session.flush()

            tuition = record.get("latest.cost.tuition.in_state") or record.get("latest.cost.tuition.out_of_state")
            housing = record.get("latest.cost.roomboard.oncampus")
            living = record.get("latest.cost.otherexpense.oncampus")
            app_fee = record.get("latest.admissions.application_fee")

            if cost_of_living:
                key = f"{(record.get('school.city') or '').lower()}|usa"
                living = cost_of_living.get(key, living)

            session.add(
                TuitionCost(
                    university_id=university.id,
                    tuition=tuition,
                    housing=housing,
                    living_cost=living,
                    application_fee=app_fee,
                    source="College Scorecard",
                    last_updated=now,
                )
            )

            session.add(
                SalaryData(
                    university_id=university.id,
                    median_salary=record.get("latest.earnings.10_yrs_after_entry.median"),
                    average_debt=record.get("latest.debt.median_grad"),
                    roi_score=None,
                )
            )

        session.commit()


if __name__ == "__main__":
    import_scorecard()
    print("Scorecard import complete.")
