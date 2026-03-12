"""
Usage examples for the graph generation MCP tool.
"""
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Example data
SALARY_DATA = [
    {'degree': 'Bachelor', 'salary': 75000, 'debt': 30000},
    {'degree': 'Master', 'salary': 95000, 'debt': 50000},
    {'degree': 'Doctoral', 'salary': 110000, 'debt': 80000}
]

UNIVERSITY_DATA = [
    {'university': 'MIT', 'bachelor_cost': 76000, 'master_cost': 78000},
    {'university': 'Stanford', 'bachelor_cost': 74000, 'master_cost': 76000},
    {'university': 'Berkeley', 'bachelor_cost': 68000, 'master_cost': 70000}
]

TIME_SERIES_DATA = [
    {'year': 2020, 'salary': 70000},
    {'year': 2021, 'salary': 73000},
    {'year': 2022, 'salary': 76000},
    {'year': 2023, 'salary': 80000},
    {'year': 2024, 'salary': 85000}
]


async def example_auto_detection():
    """Example 1: Auto-detect graph type from data."""
    server_params = StdioServerParameters(
        command="python",
        args=["server/mcp_server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("Example 1: Auto-Detection")
            print("-" * 60)
            
            result = await session.call_tool(
                "generate_graph",
                arguments={
                    "data": SALARY_DATA,
                    "title": "Average Salary by Degree Level"
                }
            )
            
            response = json.loads(result.content[0].text)
            print(f"Graph Type: {response.get('type')}")
            print(f"Data Points: {response.get('metadata', {}).get('rows')}")
            print("✓ Graph generated successfully\n")


async def example_bar_chart():
    """Example 2: Explicit bar chart."""
    server_params = StdioServerParameters(
        command="python",
        args=["server/mcp_server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("Example 2: Bar Chart")
            print("-" * 60)
            
            result = await session.call_tool(
                "generate_bar_chart",
                arguments={
                    "data": SALARY_DATA,
                    "x_column": "degree",
                    "y_column": "salary",
                    "title": "CS Salaries by Degree Level"
                }
            )
            
            response = json.loads(result.content[0].text)
            print(f"Statistics: {response.get('statistics', {})}")
            print("✓ Bar chart created\n")


async def example_comparison():
    """Example 3: Multi-series comparison."""
    server_params = StdioServerParameters(
        command="python",
        args=["server/mcp_server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("Example 3: Comparison Chart")
            print("-" * 60)
            
            result = await session.call_tool(
                "generate_comparison_chart",
                arguments={
                    "data": UNIVERSITY_DATA,
                    "category_column": "university",
                    "value_columns": ["bachelor_cost", "master_cost"],
                    "title": "Bachelor vs Master Costs by University"
                }
            )
            
            response = json.loads(result.content[0].text)
            print(f"Categories: {response.get('metadata', {}).get('categories')}")
            print("✓ Comparison chart created\n")


async def example_time_series():
    """Example 4: Time-series line graph."""
    server_params = StdioServerParameters(
        command="python",
        args=["server/mcp_server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("Example 4: Time Series")
            print("-" * 60)
            
            result = await session.call_tool(
                "generate_line_graph",
                arguments={
                    "data": TIME_SERIES_DATA,
                    "x_column": "year",
                    "y_column": "salary",
                    "title": "Salary Growth Over Time"
                }
            )
            
            response = json.loads(result.content[0].text)
            print(f"Data Shape: {response.get('metadata', {}).get('data_shape')}")
            print("✓ Time series graph created\n")


async def run_all_examples():
    """Run all examples."""
    print("=" * 60)
    print("Graph Generation MCP - Usage Examples")
    print("=" * 60)
    print()
    
    await example_auto_detection()
    await example_bar_chart()
    await example_comparison()
    await example_time_series()
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_examples())
