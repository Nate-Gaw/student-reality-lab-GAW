# Quick Start Guide - Graph Generation MCP

## Installation (5 minutes)

### 1. Install Dependencies
```bash
cd "D:/College Classes/IS219/student-reality-lab-GAW/graph-generation-mcp"
pip install -r requirements.txt
```

### 2. Test the System
```bash
python test_client.py
```

Expected output:
```
Testing Graph Generation MCP Server
====================================
1. LIST AVAILABLE TOOLS
  • generate_graph
  • generate_bar_chart
  • generate_line_graph
  ...
✅ All tests completed successfully!
```

### 3. Run the MCP Server
```bash
python server/mcp_server.py
```

## Using the Tool

### Standalone Testing
```bash
python examples/usage_examples.py
```

### Integration with Claude Desktop

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "graph-generation": {
      "command": "python",
      "args": [
        "D:/College Classes/IS219/student-reality-lab-GAW/graph-generation-mcp/server/mcp_server.py"
      ]
    }
  }
}
```

Restart Claude Desktop, then try:
```
"Generate a bar chart comparing these salaries:
Bachelor: $75,000
Master: $95,000
Doctoral: $110,000"
```

## Example Queries

### Auto-Detection
```
"Show me a graph of this data:
[{degree: 'Bachelor', salary: 75000}, 
 {degree: 'Master', salary: 95000}]"
```

### Specific Chart Type
```
"Create a line graph showing salary growth from 2020 to 2024:
2020: $70k, 2021: $73k, 2022: $76k, 2023: $80k, 2024: $85k"
```

### Comparison
```
"Compare MIT and Stanford costs:
MIT bachelor: $76k, master: $78k
Stanford bachelor: $74k, master: $76k"
```

## Available Graph Types

1. **Bar Chart** - Categorical comparisons
2. **Line Graph** - Time series/trends
3. **Scatter Plot** - Correlations
4. **Pie Chart** - Proportions
5. **Histogram** - Distributions
6. **Comparison** - Multi-series grouped bars

## Output Format

All tools return:
```json
{
  "html": "<interactive Plotly chart>",
  "figure": "{plotly figure JSON}",
  "type": "bar",
  "metadata": {
    "rows": 5,
    "columns": ["degree", "salary"],
    "x_column": "degree",
    "y_column": "salary"
  },
  "statistics": {
    "mean": 93333.33,
    "median": 95000,
    "min": 75000,
    "max": 110000
  }
}
```

## Integration with Website

See [INTEGRATION.md](INTEGRATION.md) for detailed integration patterns.

Quick option - Add graph container to Website:
```html
<div id="graph-container"></div>
```

Then inject HTML:
```javascript
document.getElementById('graph-container').innerHTML = graphResponse.html;
```

## Troubleshooting

### "Import 'plotly' could not be resolved"
```bash
pip install plotly pandas
```

### "No module named 'mcp'"
```bash
pip install mcp
```

### Graph not displaying
- Check that Plotly CDN is accessible
- Verify `include_plotlyjs='cdn'` in HTML output
- Test in browser with JavaScript enabled

## Next Steps

1. Run `test_client.py` to validate all tools
2. Try `examples/usage_examples.py` for common patterns
3. Integrate with Claude Desktop for conversational graphs
4. Combine with University Cost MCP for enhanced visualizations

---

**Setup Time**: 5 minutes  
**Dependencies**: plotly, pandas, numpy, mcp  
**Ready For**: Claude Desktop integration, Website embedding
