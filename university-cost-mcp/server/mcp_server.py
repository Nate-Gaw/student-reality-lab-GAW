"""
Main MCP server for university cost queries.
"""
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio
from typing import Any, Sequence
import json
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data.storage.database import DatabaseManager
from server.query_handler import QueryHandler

# Initialize database and query handler
db_manager = DatabaseManager()
db_manager.create_tables()
query_handler = QueryHandler(db_manager)

# Create MCP server
app = Server("university-cost-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="get_university_cost",
            description="Get detailed cost breakdown for a specific university and degree level",
            inputSchema={
                "type": "object",
                "properties": {
                    "university_name": {
                        "type": "string",
                        "description": "Name of the university"
                    },
                    "degree_level": {
                        "type": "string",
                        "enum": ["bachelor", "master", "doctoral"],
                        "description": "Degree level (bachelor, master, or doctoral)"
                    },
                    "student_type": {
                        "type": "string",
                        "enum": ["domestic", "international"],
                        "description": "Student residency status",
                        "default": "international"
                    }
                },
                "required": ["university_name", "degree_level"]
            }
        ),
        Tool(
            name="get_universities_by_country",
            description="Get all universities in a specific country with their costs",
            inputSchema={
                "type": "object",
                "properties": {
                    "country": {
                        "type": "string",
                        "description": "Country name"
                    },
                    "degree_level": {
                        "type": "string",
                        "enum": ["bachelor", "master", "doctoral"],
                        "description": "Filter by degree level (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 50
                    }
                },
                "required": ["country"]
            }
        ),
        Tool(
            name="compare_university_costs",
            description="Compare costs across multiple universities",
            inputSchema={
                "type": "object",
                "properties": {
                    "university_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of university names to compare"
                    },
                    "degree_level": {
                        "type": "string",
                        "enum": ["bachelor", "master", "doctoral"],
                        "description": "Degree level for comparison"
                    },
                    "student_type": {
                        "type": "string",
                        "enum": ["domestic", "international"],
                        "description": "Student residency status",
                        "default": "international"
                    }
                },
                "required": ["university_names", "degree_level"]
            }
        ),
        Tool(
            name="search_universities",
            description="Search universities by name, location, or program",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "Search term (university name, city, or country)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 20
                    }
                },
                "required": ["search_term"]
            }
        ),
        Tool(
            name="get_cost_statistics",
            description="Get statistical analysis of university costs by region or program type",
            inputSchema={
                "type": "object",
                "properties": {
                    "country": {
                        "type": "string",
                        "description": "Country to analyze (optional)"
                    },
                    "degree_level": {
                        "type": "string",
                        "enum": ["bachelor", "master", "doctoral"],
                        "description": "Degree level to analyze (optional)"
                    }
                },
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls."""
    
    try:
        if name == "get_university_cost":
            result = query_handler.get_university_cost(
                university_name=arguments["university_name"],
                degree_level=arguments["degree_level"],
                student_type=arguments.get("student_type", "international")
            )
        
        elif name == "get_universities_by_country":
            result = query_handler.get_universities_by_country(
                country=arguments["country"],
                degree_level=arguments.get("degree_level"),
                limit=arguments.get("limit", 50)
            )
        
        elif name == "compare_university_costs":
            result = query_handler.compare_university_costs(
                university_names=arguments["university_names"],
                degree_level=arguments["degree_level"],
                student_type=arguments.get("student_type", "international")
            )
        
        elif name == "search_universities":
            result = query_handler.search_universities(
                search_term=arguments["search_term"],
                limit=arguments.get("limit", 20)
            )
        
        elif name == "get_cost_statistics":
            result = query_handler.get_cost_statistics(
                country=arguments.get("country"),
                degree_level=arguments.get("degree_level")
            )
        
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]


async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    print("Starting University Cost MCP Server...", file=sys.stderr)
    asyncio.run(main())
