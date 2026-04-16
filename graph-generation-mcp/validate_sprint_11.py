import json

from server.graph_generator import GraphGenerator


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate() -> None:
    generator = GraphGenerator()

    auto = generator.generate_graph(
        data=[
            {"degree": "Bachelor", "salary": 75000},
            {"degree": "Master", "salary": 95000},
            {"degree": "Doctoral", "salary": 110000},
        ],
        title="Average CS Salary by Degree",
    )
    _assert(auto.get("type") in ["bar", "line", "scatter", "pie", "histogram"], "auto-detect graph type invalid")

    bar = generator.generate_graph(
        data=[
            {"university": "MIT", "cost": 76000},
            {"university": "Stanford", "cost": 74000},
        ],
        graph_type="bar",
        x_column="university",
        y_column="cost",
        title="Annual Cost",
    )
    _assert(bar.get("type") == "bar", "bar chart type mismatch")

    line = generator.generate_graph(
        data=[
            {"year": 2020, "salary": 70000},
            {"year": 2021, "salary": 73000},
            {"year": 2022, "salary": 76000},
        ],
        graph_type="line",
        x_column="year",
        y_column="salary",
        title="Salary Growth",
    )
    _assert(line.get("type") == "line", "line graph type mismatch")

    scatter = generator.generate_correlation_plot(
        data=[
            {"debt": 30000, "salary": 75000},
            {"debt": 50000, "salary": 95000},
            {"debt": 80000, "salary": 110000},
        ],
        variable_x="debt",
        variable_y="salary",
        title="Debt vs Salary",
    )
    _assert(scatter.get("type") == "scatter", "scatter plot type mismatch")

    pie = generator.generate_graph(
        data=[
            {"expense": "Tuition", "amount": 57000},
            {"expense": "Housing", "amount": 12000},
        ],
        graph_type="pie",
        x_column="expense",
        y_column="amount",
        title="Cost Breakdown",
    )
    _assert(pie.get("type") == "pie", "pie chart type mismatch")

    histogram = generator.generate_graph(
        data=[{"salary": s} for s in [70000, 72000, 75000, 78000, 80000]],
        graph_type="histogram",
        x_column="salary",
        title="Salary Distribution",
    )
    _assert(histogram.get("type") == "histogram", "histogram type mismatch")

    comparison = generator.generate_comparison_chart(
        data=[
            {"university": "MIT", "bachelor": 76000, "master": 78000},
            {"university": "Stanford", "bachelor": 74000, "master": 76000},
        ],
        category_column="university",
        value_columns=["bachelor", "master"],
        title="Bachelor vs Master Costs",
    )
    _assert(comparison.get("type") == "comparison", "comparison chart type mismatch")

    print(json.dumps({"status": "ok", "sprint": 11}, indent=2))


if __name__ == "__main__":
    validate()
