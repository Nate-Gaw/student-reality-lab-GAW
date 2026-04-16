from __future__ import annotations

from typing import Dict, List


def calculate_total_cost(costs: Dict) -> float:
    return sum(float(costs.get(key) or 0) for key in ["tuition", "housing", "living_cost"])


def compute_break_even_years(cost: float, salary: float) -> float | None:
    if salary <= 0:
        return None
    return round(cost / salary, 2)


def compute_roi(cost: float, salary: float, horizon_years: int = 10) -> float:
    return (salary * horizon_years) - cost


def build_roi_summary(profile: Dict) -> Dict:
    costs = profile.get("costs", {})
    salary = profile.get("salary", {})

    total_cost = calculate_total_cost(costs)
    median_salary = float(salary.get("median_salary") or 0)

    return {
        "total_cost": total_cost,
        "median_salary": median_salary,
        "break_even_years": compute_break_even_years(total_cost, median_salary),
        "roi_10_year": compute_roi(total_cost, median_salary, horizon_years=10),
    }


def attach_roi(profiles: List[Dict]) -> List[Dict]:
    enriched = []
    for profile in profiles:
        roi = build_roi_summary(profile)
        profile = {**profile, "roi": roi}
        enriched.append(profile)
    return enriched


def rank_by_roi(profiles: List[Dict]) -> List[Dict]:
    enriched = attach_roi(profiles)
    return sorted(enriched, key=lambda p: p["roi"]["roi_10_year"], reverse=True)
