from __future__ import annotations

from typing import Dict, List

from sqlalchemy import select

from backend.cache.redis_cache import cache
from backend.database.models import SalaryData, SessionLocal, TuitionCost, University


def _build_profile(row: University, tuition: TuitionCost | None, salary: SalaryData | None) -> Dict:
    return {
        "university_name": row.name,
        "country": row.country,
        "city": row.city,
        "website": row.website,
        "costs": {
            "tuition": tuition.tuition if tuition else None,
            "housing": tuition.housing if tuition else None,
            "living_cost": tuition.living_cost if tuition else None,
            "application_fee": tuition.application_fee if tuition else None,
            "source": tuition.source if tuition else None,
            "last_updated": tuition.last_updated if tuition else None,
        },
        "salary": {
            "median_salary": salary.median_salary if salary else None,
            "average_debt": salary.average_debt if salary else None,
            "roi_score": salary.roi_score if salary else None,
        },
    }


def get_university_profile(name: str) -> Dict | None:
    if not name:
        return None

    cache_key = f"university_profile:{name.lower()}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    with SessionLocal() as session:
        university = session.scalar(select(University).where(University.name == name))
        if not university:
            return None

        tuition = session.scalar(
            select(TuitionCost)
            .where(TuitionCost.university_id == university.id)
            .order_by(TuitionCost.last_updated.desc(), TuitionCost.id.desc())
        )
        salary = session.scalar(
            select(SalaryData)
            .where(SalaryData.university_id == university.id)
            .order_by(SalaryData.id.desc())
        )

    profile = _build_profile(university, tuition, salary)
    cache.set(cache_key, profile, ttl_seconds=1800)
    return profile


def get_university_profiles(names: List[str]) -> List[Dict]:
    profiles = []
    missing = []
    for name in names:
        if not name:
            continue
        cache_key = f"university_profile:{name.lower()}"
        cached = cache.get(cache_key)
        if cached:
            profiles.append(cached)
            continue
        missing.append(name)

    if not missing:
        return profiles

    with SessionLocal() as session:
        universities = (
            session.execute(select(University).where(University.name.in_(missing))).scalars().all()
        )
        if not universities:
            return profiles

        university_ids = [row.id for row in universities]
        tuition_rows = (
            session.execute(
                select(TuitionCost)
                .where(TuitionCost.university_id.in_(university_ids))
                .order_by(TuitionCost.last_updated.desc(), TuitionCost.id.desc())
            )
            .scalars()
            .all()
        )
        salary_rows = (
            session.execute(
                select(SalaryData)
                .where(SalaryData.university_id.in_(university_ids))
                .order_by(SalaryData.id.desc())
            )
            .scalars()
            .all()
        )

        latest_tuition: dict[int, TuitionCost] = {}
        for row in tuition_rows:
            if row.university_id not in latest_tuition:
                latest_tuition[row.university_id] = row

        latest_salary: dict[int, SalaryData] = {}
        for row in salary_rows:
            if row.university_id not in latest_salary:
                latest_salary[row.university_id] = row

        for university in universities:
            tuition = latest_tuition.get(university.id)
            salary = latest_salary.get(university.id)
            profile = _build_profile(university, tuition, salary)
            cache.set(f"university_profile:{university.name.lower()}", profile, ttl_seconds=1800)
            profiles.append(profile)

    return profiles
