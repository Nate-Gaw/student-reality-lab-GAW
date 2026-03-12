# Graph Generation MCP Tool

A Model Context Protocol (MCP) server that generates interactive visualizations dynamically based on data inputs and user queries. Built with Plotly for modern, interactive charts.

## Features

- **Intelligent Graph Selection** - Automatically chooses optimal visualization based on data characteristics
- **Interactive Visualizations** - Hover, zoom, pan, and export capabilities
- **Multiple Chart Types** - Bar, line, scatter, pie, histogram, and more
- **Flexible Input** - Accepts JSON, CSV, DataFrame dictionaries
- **Data Processing** - Built-in Pandas integration for data manipulation
- **MCP Integration** - Works with Claude Desktop and other MCP clients

## Supported Graph Types

1. **Bar Charts** - Categorical comparisons
2. **Line Graphs** - Time-series trends
3. **Scatter Plots** - Correlation analysis
4. **Pie Charts** - Proportional breakdowns
5. **Histograms** - Distribution analysis
6. **Box Plots** - Statistical distributions
7. **Heatmaps** - Correlation matrices

## Architecture

```
graph-generation-mcp/
├── server/
│   ├── mcp_server.py          # MCP protocol server
│   └── graph_generator.py     # Graph generation logic
├── visualizations/
│   ├── plotly_engine.py       # Plotly wrapper
│   ├── graph_types.py         # Graph type definitions
│   └── data_processor.py      # Data cleaning/preparation
├── config/
│   └── graph_config.json      # Default styling
├── examples/
│   ├── sample_data.csv        # Example datasets
│   └── usage_examples.py      # Usage patterns
└── requirements.txt
```

## Quick Start

```bash
cd graph-generation-mcp
pip install -r requirements.txt
python server/mcp_server.py
```

## MCP Tools Exposed

1. **generate_graph** - Auto-detects optimal graph type
2. **generate_bar_chart** - Explicit bar chart creation
3. **generate_line_graph** - Time-series visualization
4. **generate_scatter_plot** - Correlation analysis
5. **generate_pie_chart** - Proportional data
6. **generate_histogram** - Distribution visualization
7. **generate_comparison_chart** - Side-by-side comparisons

## Usage Example

```python
# Via MCP
result = await mcp_client.call_tool('generate_graph', {
    'data': [
        {'category': 'Bachelor', 'salary': 75000},
        {'category': 'Master', 'salary': 95000}
    ],
    'x_column': 'category',
    'y_column': 'salary',
    'title': 'Average Salary by Degree'
})

# Returns interactive HTML chart
```

## Integration with Website

The graph tool can enhance the existing financial advisor:
- Visualize 30-year projections
- Compare university costs
- Show break-even timelines
- Display salary trends

See [INTEGRATION.md](INTEGRATION.md) for details.
