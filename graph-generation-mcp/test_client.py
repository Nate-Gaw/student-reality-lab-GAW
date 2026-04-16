"""
Test client for the Graph Generation MCP server.
"""
import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_graph_mcp_server():
    """Test all graph generation tools."""
    
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server/mcp_server.py"],
    )
    
    print("Connecting to Graph Generation MCP server...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("\n" + "=" * 60)
            print("Testing Graph Generation MCP Server")
            print("=" * 60)
            
            # Test 1: List tools
            print("\n1. LIST AVAILABLE TOOLS")
            print("-" * 60)
            tools = await session.list_tools()
            for tool in tools:
                print(f"  • {tool.name}")
            print(f"\nTotal tools: {len(tools)}")
            
            # Test 2: Auto-detect graph (salary by degree)
            print("\n2. AUTO-DETECT GRAPH TYPE")
            print("-" * 60)
            result = await session.call_tool(
                "generate_graph",
                arguments={
                    "data": [
                        {'degree': 'Bachelor', 'salary': 75000},
                        {'degree': 'Master', 'salary': 95000},
                        {'degree': 'Doctoral', 'salary': 110000}
                    ],
                    "title": "Average CS Salary by Degree"
                }
            )
            response = json.loads(result.content[0].text)
            print(f"Detected Type: {response.get('type')}")
            print(f"Data Points: {response.get('metadata', {}).get('rows')}")
            if 'statistics' in response:
                stats = response['statistics']
                print(f"Mean: ${stats['mean']:,.0f}")
                print(f"Median: ${stats['median']:,.0f}")
            
            # Test 3: Bar chart
            print("\n3. GENERATE BAR CHART")
            print("-" * 60)
            result = await session.call_tool(
                "generate_bar_chart",
                arguments={
                    "data": [
                        {'university': 'MIT', 'cost': 76000},
                        {'university': 'Stanford', 'cost': 74000},
                        {'university': 'Berkeley', 'cost': 68000},
                        {'university': 'Georgia Tech', 'cost': 55000}
                    ],
                    "x_column": "university",
                    "y_column": "cost",
                    "title": "Annual Cost by University"
                }
            )
            response = json.loads(result.content[0].text)
            print(f"Type: {response.get('type')}")
            print(f"Universities: {response.get('metadata', {}).get('rows')}")
            
            # Test 4: Line graph (time series)
            print("\n4. GENERATE LINE GRAPH")
            print("-" * 60)
            result = await session.call_tool(
                "generate_line_graph",
                arguments={
                    "data": [
                        {'year': 2020, 'salary': 70000},
                        {'year': 2021, 'salary': 73000},
                        {'year': 2022, 'salary': 76000},
                        {'year': 2023, 'salary': 80000},
                        {'year': 2024, 'salary': 85000}
                    ],
                    "x_column": "year",
                    "y_column": "salary",
                    "title": "CS Salary Growth 2020-2024"
                }
            )
            response = json.loads(result.content[0].text)
            print(f"Type: {response.get('type')}")
            print(f"Years Tracked: {response.get('metadata', {}).get('rows')}")
            
            # Test 5: Scatter plot
            print("\n5. GENERATE SCATTER PLOT")
            print("-" * 60)
            result = await session.call_tool(
                "generate_scatter_plot",
                arguments={
                    "data": [
                        {'debt': 30000, 'salary': 75000},
                        {'debt': 50000, 'salary': 95000},
                        {'debt': 80000, 'salary': 110000},
                        {'debt': 35000, 'salary': 78000},
                        {'debt': 55000, 'salary': 98000}
                    ],
                    "x_column": "debt",
                    "y_column": "salary",
                    "title": "Debt vs Salary Correlation"
                }
            )
            response = json.loads(result.content[0].text)
            print(f"Type: {response.get('type')}")
            print(f"Correlation: {response.get('correlation', 0):.3f}")
            
            # Test 6: Pie chart
            print("\n6. GENERATE PIE CHART")
            print("-" * 60)
            result = await session.call_tool(
                "generate_pie_chart",
                arguments={
                    "data": [
                        {'expense': 'Tuition', 'amount': 57000},
                        {'expense': 'Housing', 'amount': 12000},
                        {'expense': 'Food', 'amount': 5000},
                        {'expense': 'Books', 'amount': 1000},
                        {'expense': 'Other', 'amount': 3000}
                    ],
                    "x_column": "expense",
                    "y_column": "amount",
                    "title": "Cost Breakdown"
                }
            )
            response = json.loads(result.content[0].text)
            print(f"Type: {response.get('type')}")
            print(f"Categories: {response.get('metadata', {}).get('rows')}")
            
            # Test 7: Histogram
            print("\n7. GENERATE HISTOGRAM")
            print("-" * 60)
            salaries = [
                {'salary': s} for s in 
                [70000, 72000, 75000, 78000, 80000, 82000, 85000, 88000, 90000,
                 95000, 98000, 100000, 105000, 110000, 115000, 120000]
            ]
            result = await session.call_tool(
                "generate_histogram",
                arguments={
                    "data": salaries,
                    "x_column": "salary",
                    "title": "CS Salary Distribution"
                }
            )
            response = json.loads(result.content[0].text)
            print(f"Type: {response.get('type')}")
            print(f"Sample Size: {response.get('metadata', {}).get('rows')}")
            
            # Test 8: Comparison chart
            print("\n8. GENERATE COMPARISON CHART")
            print("-" * 60)
            result = await session.call_tool(
                "generate_comparison_chart",
                arguments={
                    "data": [
                        {'university': 'MIT', 'bachelor': 76000, 'master': 78000},
                        {'university': 'Stanford', 'bachelor': 74000, 'master': 76000},
                        {'university': 'Berkeley', 'bachelor': 68000, 'master': 70000}
                    ],
                    "category_column": "university",
                    "value_columns": ["bachelor", "master"],
                    "title": "Bachelor vs Master Costs"
                }
            )
            response = json.loads(result.content[0].text)
            print(f"Type: {response.get('type')}")
            print(f"Comparing: {response.get('metadata', {}).get('value_columns')}")
            
            print("\n" + "=" * 60)
            print("✅ All tests completed successfully!")
            print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_graph_mcp_server())
