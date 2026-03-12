"""
MCP server for graph generation.
"""
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio
from typing import Any, Sequence
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from server.graph_generator import GraphGenerator

# Initialize graph generator
graph_generator = GraphGenerator()

# Create MCP server
app = Server("graph-generation-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="generate_graph",
            description="Generate a graph with automatic type detection. Accepts various data formats and intelligently selects the best visualization.",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "description": "Data as list of dicts, single dict, or DataFrame-like structure",
                        "oneOf": [
                            {"type": "array", "items": {"type": "object"}},
                            {"type": "object"}
                        ]
                    },
                    "x_column": {
                        "type": "string",
                        "description": "Column name for X-axis (auto-detected if omitted)"
                    },
                    "y_column": {
                        "type": "string",
                        "description": "Column name for Y-axis (auto-detected if omitted)"
                    },
                    "graph_type": {
                        "type": "string",
                        "enum": ["bar", "line", "scatter", "pie", "histogram", "box", "heatmap"],
                        "description": "Explicit graph type (auto-detected if omitted)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Graph title"
                    },
                    "color_by": {
                        "type": "string",
                        "description": "Column to color/group by"
                    },
                    "aggregation": {
                        "type": "string",
                        "enum": ["mean", "sum", "count", "median", "min", "max"],
                        "description": "Aggregation method if grouping data"
                    }
                },
                "required": ["data"]
            }
        ),
        Tool(
            name="generate_bar_chart",
            description="Generate a bar chart for categorical comparisons",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "description": "Data as list of dicts or DataFrame structure",
                        "oneOf": [
                            {"type": "array", "items": {"type": "object"}},
                            {"type": "object"}
                        ]
                    },
                    "x_column": {
                        "type": "string",
                        "description": "Category column (X-axis)"
                    },
                    "y_column": {
                        "type": "string",
                        "description": "Value column (Y-axis)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Chart title"
                    },
                    "orientation": {
                        "type": "string",
                        "enum": ["v", "h"],
                        "description": "Bar orientation: v=vertical, h=horizontal",
                        "default": "v"
                    }
                },
                "required": ["data", "x_column", "y_column"]
            }
        ),
        Tool(
            name="generate_line_graph",
            description="Generate a line graph for time-series or trend data",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "description": "Data with time/sequential information",
                        "type": "array",
                        "items": {"type": "object"}
                    },
                    "x_column": {
                        "type": "string",
                        "description": "Time/sequence column (X-axis)"
                    },
                    "y_column": {
                        "type": "string",
                        "description": "Value column (Y-axis)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Chart title"
                    }
                },
                "required": ["data", "x_column", "y_column"]
            }
        ),
        Tool(
            name="generate_scatter_plot",
            description="Generate a scatter plot for correlation analysis between two numeric variables",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {"type": "object"}
                    },
                    "x_column": {
                        "type": "string",
                        "description": "X variable (numeric)"
                    },
                    "y_column": {
                        "type": "string",
                        "description": "Y variable (numeric)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Chart title"
                    },
                    "color_by": {
                        "type": "string",
                        "description": "Column to color points by"
                    }
                },
                "required": ["data", "x_column", "y_column"]
            }
        ),
        Tool(
            name="generate_pie_chart",
            description="Generate a pie chart for proportional breakdown",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {"type": "object"}
                    },
                    "x_column": {
                        "type": "string",
                        "description": "Category column (labels)"
                    },
                    "y_column": {
                        "type": "string",
                        "description": "Value column (sizes)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Chart title"
                    }
                },
                "required": ["data", "x_column", "y_column"]
            }
        ),
        Tool(
            name="generate_histogram",
            description="Generate a histogram for distribution analysis of a single numeric variable",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {"type": "object"}
                    },
                    "x_column": {
                        "type": "string",
                        "description": "Numeric column to analyze"
                    },
                    "title": {
                        "type": "string",
                        "description": "Chart title"
                    },
                    "bins": {
                        "type": "integer",
                        "description": "Number of bins",
                        "default": 30
                    }
                },
                "required": ["data", "x_column"]
            }
        ),
        Tool(
            name="generate_comparison_chart",
            description="Generate a grouped bar chart comparing multiple values across categories",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {"type": "object"}
                    },
                    "category_column": {
                        "type": "string",
                        "description": "Column with categories to compare (e.g., 'University')"
                    },
                    "value_columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of columns to compare (e.g., ['Bachelor', 'Master'])"
                    },
                    "title": {
                        "type": "string",
                        "description": "Chart title"
                    }
                },
                "required": ["data", "category_column", "value_columns"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls."""
    
    try:
        if name == "generate_graph":
            result = graph_generator.generate_graph(**arguments)
        
        elif name == "generate_bar_chart":
            result = graph_generator.generate_graph(
                graph_type="bar",
                **arguments
            )
        
        elif name == "generate_line_graph":
            result = graph_generator.generate_graph(
                graph_type="line",
                **arguments
            )
        
        elif name == "generate_scatter_plot":
            result = graph_generator.generate_correlation_plot(
                data=arguments["data"],
                variable_x=arguments["x_column"],
                variable_y=arguments["y_column"],
                title=arguments.get("title")
            )
        
        elif name == "generate_pie_chart":
            result = graph_generator.generate_graph(
                graph_type="pie",
                **arguments
            )
        
        elif name == "generate_histogram":
            result = graph_generator.generate_graph(
                graph_type="histogram",
                **arguments
            )
        
        elif name == "generate_comparison_chart":
            result = graph_generator.generate_comparison_chart(**arguments)
        
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
    print("Starting Graph Generation MCP Server...", file=sys.stderr)
    asyncio.run(main())
