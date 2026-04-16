import json
from pathlib import Path

from server.query_handler import QueryHandler
from data.storage.database import DatabaseManager


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate() -> None:
    db = DatabaseManager()
    db.create_tables()
    handler = QueryHandler(db)

    # Tool 1: get_university_cost
    mit = handler.get_university_cost("Massachusetts Institute of Technology", "bachelor", "international")
    _assert("university_name" in mit, "get_university_cost missing university_name")
    _assert(mit.get("degree_level") == "bachelor", "get_university_cost degree_level mismatch")
    _assert("costs" in mit and isinstance(mit["costs"], dict), "get_university_cost missing costs")

    # Tool 2: get_universities_by_country
    us_list = handler.get_universities_by_country("United States", limit=5)
    _assert("universities" in us_list, "get_universities_by_country missing universities")
    _assert(isinstance(us_list["universities"], list), "get_universities_by_country universities not list")

    # Tool 3: compare_university_costs
    comparison = handler.compare_university_costs(
        ["Massachusetts Institute of Technology", "University of Oxford", "Technical University of Munich"],
        degree_level="bachelor",
        student_type="international",
    )
    _assert("universities" in comparison, "compare_university_costs missing universities")
    _assert(len(comparison["universities"]) >= 2, "compare_university_costs returned too few")

    # Tool 4: search_universities
    search = handler.search_universities("Oxford", limit=5)
    _assert("results" in search, "search_universities missing results")

    # Tool 5: get_cost_statistics
    stats = handler.get_cost_statistics(degree_level="bachelor")
    _assert("sample_size" in stats, "get_cost_statistics missing sample_size")

    print(json.dumps({"status": "ok", "sprint": 10}, indent=2))


if __name__ == "__main__":
    validate()
