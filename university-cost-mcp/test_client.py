"""
Test client for the University Cost MCP server.
"""
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_server():
    """Test the MCP server with various queries."""
    
    # Start MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["server/mcp_server.py"],
    )
    
    print("Connecting to MCP server...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            print("\n" + "=" * 60)
            print("Testing University Cost MCP Server")
            print("=" * 60)
            
            # Test 1: List available tools
            print("\n1. LIST AVAILABLE TOOLS")
            print("-" * 60)
            tools = await session.list_tools()
            for tool in tools:
                print(f"  • {tool.name}")
                print(f"    {tool.description}")
            
            # Test 2: Get university cost
            print("\n2. GET UNIVERSITY COST")
            print("-" * 60)
            result = await session.call_tool(
                "get_university_cost",
                arguments={
                    "university_name": "Massachusetts Institute of Technology",
                    "degree_level": "bachelor",
                    "student_type": "international"
                }
            )
            print(json.dumps(json.loads(result.content[0].text), indent=2))
            
            # Test 3: Search universities
            print("\n3. SEARCH UNIVERSITIES")
            print("-" * 60)
            result = await session.call_tool(
                "search_universities",
                arguments={"search_term": "Oxford", "limit": 5}
            )
            print(json.dumps(json.loads(result.content[0].text), indent=2))
            
            # Test 4: Compare costs
            print("\n4. COMPARE UNIVERSITY COSTS")
            print("-" * 60)
            result = await session.call_tool(
                "compare_university_costs",
                arguments={
                    "university_names": [
                        "Massachusetts Institute of Technology",
                        "University of Oxford",
                        "Technical University of Munich"
                    ],
                    "degree_level": "bachelor",
                    "student_type": "international"
                }
            )
            comparison = json.loads(result.content[0].text)
            print(json.dumps(comparison, indent=2))
            
            # Test 5: Get universities by country
            print("\n5. GET UNIVERSITIES BY COUNTRY")
            print("-" * 60)
            result = await session.call_tool(
                "get_universities_by_country",
                arguments={"country": "United States", "limit": 5}
            )
            print(json.dumps(json.loads(result.content[0].text), indent=2))
            
            # Test 6: Get cost statistics
            print("\n6. GET COST STATISTICS")
            print("-" * 60)
            result = await session.call_tool(
                "get_cost_statistics",
                arguments={"degree_level": "bachelor"}
            )
            print(json.dumps(json.loads(result.content[0].text), indent=2))
            
            print("\n" + "=" * 60)
            print("All tests completed!")
            print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
