from __future__ import annotations

from typing import Any, Dict, List

from flask import Blueprint, jsonify, request

from backend.services.university_service import get_university_profiles
from backend.services.roi_engine import attach_roi


graphs_bp = Blueprint("graphs", __name__)


def build_graph_from_profiles(profiles: List[Dict[str, Any]]) -> Dict[str, Any] | None:
    if not profiles:
        return None

    if len(profiles) >= 2:
        labels = [profile["university_name"] for profile in profiles]
        tuition = [profile["roi"]["total_cost"] for profile in profiles]
        salaries = [profile["roi"]["median_salary"] for profile in profiles]

        return {
            "title": "Tuition vs Median Salary",
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": [
                    {
                        "label": "Total Annual Cost",
                        "data": tuition,
                        "backgroundColor": "rgba(14, 165, 168, 0.35)",
                        "borderColor": "rgba(14, 165, 168, 0.8)",
                        "borderWidth": 1,
                    },
                    {
                        "label": "Median Salary",
                        "data": salaries,
                        "backgroundColor": "rgba(56, 189, 248, 0.35)",
                        "borderColor": "rgba(56, 189, 248, 0.8)",
                        "borderWidth": 1,
                    },
                ],
            },
            "options": {
                "responsive": True,
                "scales": {
                    "y": {
                        "beginAtZero": True,
                    }
                },
                "plugins": {
                    "legend": {"position": "bottom"},
                },
            },
        }

    profile = profiles[0]
    costs = profile.get("costs", {})
    labels = ["Tuition", "Housing", "Living", "Application"]
    values = [
        costs.get("tuition") or 0,
        costs.get("housing") or 0,
        costs.get("living_cost") or 0,
        costs.get("application_fee") or 0,
    ]

    return {
        "title": f"{profile['university_name']} Cost Breakdown",
        "type": "pie",
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "label": "Annual Cost",
                    "data": values,
                    "backgroundColor": [
                        "rgba(14, 165, 168, 0.6)",
                        "rgba(56, 189, 248, 0.6)",
                        "rgba(99, 102, 241, 0.6)",
                        "rgba(248, 113, 113, 0.6)",
                    ],
                    "borderWidth": 1,
                }
            ],
        },
        "options": {
            "responsive": True,
            "plugins": {"legend": {"position": "bottom"}},
        },
    }


@graphs_bp.post("/api/graphs")
def graphs() -> Any:
    body = request.get_json(silent=True) or {}
    names = body.get("universities", [])
    if not names:
        return jsonify({"error": "Missing universities"}), 400

    profiles = attach_roi(get_university_profiles(names))
    graph = build_graph_from_profiles(profiles)
    return jsonify({"graph": graph})
