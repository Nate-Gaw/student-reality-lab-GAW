# Graph Generation MCP - Integration Guide

## Overview

The Graph Generation MCP tool integrates seamlessly with both the **Website Financial Advisor** and the **University Cost MCP** to provide dynamic, interactive visualizations of financial data.

## Architecture Integration

```
┌─────────────────────────────────────────────────────────┐
│                 User (Claude Desktop)                    │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Website    │  │ University   │  │    Graph     │
│   (OpenAI)   │  │  Cost MCP    │  │ Generation   │
│              │  │              │  │     MCP      │
│ • ROI Calc   │  │ • API Data   │  │              │
│ • Break-even │  │ • Costs      │  │ • Plotly     │
│ • Projections│  │ • Stats      │  │ • Charts     │
└──────────────┘  └──────────────┘  └──────────────┘
        │                 │                 │
        └─────────────────┴─────────────────┘
                          │
                          ▼
              ┌────────────────────┐
              │   User Interface   │
              │  - Text Responses  │
              │  - Interactive     │
              │    Graphs          │
              │  - Key Notes       │
              └────────────────────┘
```

## Use Case 1: Visualize 30-Year ROI Projections

### Current State (Website Only)
User asks: "Should I get a master's degree?"
- Website calculates break-even year
- Returns text summary
- Key notes extracted

### Enhanced with Graph MCP
User asks: "Show me the 30-year earnings comparison"
- Website calculates projections
- Claude calls **Graph MCP** with projection data
- Returns **interactive line graph** showing:
  - Bachelor cumulative earnings (line 1)
  - Master cumulative earnings (line 2)  
  - Break-even point highlighted
  - 30-year advantage annotated

### Implementation

```javascript
// Website generates projection data
const projectionData = [];
for (let year = 1; year <= 30; year++) {
  projectionData.push({
    year,
    bachelor_cumulative: bachelorCumulative[year],
    master_cumulative: masterCumulative[year]
  });
}

// Claude calls Graph MCP
const graphResult = await graphMCP.call_tool('generate_comparison_chart', {
  data: projectionData,
  category_column: 'year',
  value_columns: ['bachelor_cumulative', 'master_cumulative'],
  title: '30-Year Earnings Projection: Bachelor vs Master'
});

// Display interactive graph alongside text response
```

## Use Case 2: Compare University Costs Visually

### Workflow
1. User: "Compare costs at MIT, Stanford, and Berkeley"
2. Claude calls **University Cost MCP** to get data:
   ```json
   [
     {"university": "MIT", "bachelor": 76000, "master": 78000},
     {"university": "Stanford", "bachelor": 74000, "master": 76000},
     {"university": "Berkeley", "bachelor": 68000, "master": 70000}
   ]
   ```
3. Claude calls **Graph MCP** to visualize:
   ```python
   generate_comparison_chart(
     data=university_costs,
     category_column='university',
     value_columns=['bachelor', 'master'],
     title='Annual Cost: Bachelor vs Master Programs'
   )
   ```
4. Returns grouped bar chart showing:
   - Each university on X-axis
   - Bachelor/Master bars side-by-side
   - Hover shows exact costs
   - Color-coded by degree level

## Use Case 3: Salary Distribution Analysis

### Scenario
User: "What's the typical salary range for CS master's graduates?"

### Flow
1. **University Cost MCP** retrieves salary data for multiple universities
2. **Graph MCP** generates histogram:
   ```python
   generate_histogram(
     data=salary_data,
     x_column='salary',
     title='CS Master\'s Salary Distribution',
     bins=20
   )
   ```
3. Returns interactive histogram showing:
   - Frequency distribution
   - Mean/median lines
   - Quartile markers
   - Hover for exact bin counts

## Use Case 4: Break-Even Timeline Visualization

### Current Website Calculation
```javascript
const breakEvenYear = 10; // Calculated by Website
const yearlyAdvantage = (masterSalary - bachelorSalary); // $20,000
```

### Enhanced Visualization
```python
# Generate break-even timeline
timeline_data = [
  {'year': year, 'net_advantage': net_cumulative[year]}
  for year in range(1, 31)
]

graph_mcp.call_tool('generate_line_graph', {
  data: timeline_data,
  x_column: 'year',
  y_column: 'net_advantage',
  title: 'Net Financial Advantage Over Time'
})
```

Shows:
- Negative advantage during master's program (years 1-6)
- Break-even point where line crosses zero axis
- Cumulative advantage growth (years 10-30)
- Shaded regions for clarity

## Use Case 5: Cost Breakdown Pie Chart

### Scenario
User: "What makes up the total cost of MIT?"

### Implementation
```python
cost_breakdown = [
  {'expense': 'Tuition', 'amount': 57590},
  {'expense': 'Housing', 'amount': 12680},
  {'expense': 'Living', 'amount': 5540},
  {'expense': 'Books', 'amount': 840},
  {'expense': 'Fees', 'amount': 384}
]

generate_pie_chart(
  data=cost_breakdown,
  x_column='expense',
  y_column='amount',
  title='MIT Annual Cost Breakdown'
)
```

Returns interactive pie chart with:
- Proportional slices
- Percentage labels
- Hover for exact amounts
- Legend with totals

## Integration Methods

### Method 1: Claude Desktop Orchestration (Recommended)

Claude acts as coordinator between all three systems:

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "university-cost": {
      "command": "python",
      "args": ["path/to/university-cost-mcp/server/mcp_server.py"]
    },
    "graph-generation": {
      "command": "python",
      "args": ["path/to/graph-generation-mcp/server/mcp_server.py"]
    }
  }
}
```

**User query flow**:
```
User: "Show me a graph comparing MIT and Stanford costs"
  ↓
Claude: [calls university-cost MCP] → Gets data
  ↓
Claude: [calls graph-generation MCP with data] → Gets chart
  ↓
Claude: Returns text + interactive graph
```

### Method 2: Website Direct Integration

Website can call Graph MCP directly via subprocess:

```javascript
// In Website main.js
async function generateProjectionGraph(projectionData) {
  const response = await fetch('http://localhost:8000/api/graph', {
    method: 'POST',
    body: JSON.stringify({
      tool: 'generate_line_graph',
      data: projectionData,
      x_column: 'year',
      y_column: 'cumulative_earnings'
    })
  });
  
  const graph = await response.json();
  
  // Inject HTML into page
  document.getElementById('graph-container').innerHTML = graph.html;
}
```

### Method 3: Python Bridge Script

Create a bridge script that combines all three:

```python
# bridge.py
from university_cost_mcp.server.query_handler import QueryHandler
from graph_generation_mcp.server.graph_generator import GraphGenerator

class IntegratedAnalyzer:
    def __init__(self):
        self.cost_handler = QueryHandler()
        self.graph_gen = GraphGenerator()
    
    def analyze_university(self, name, degree):
        # Get cost data
        cost_data = self.cost_handler.get_university_cost(name, degree)
        
        # Generate visualization
        graph = self.graph_gen.generate_graph(
            data=[cost_data],
            x_column='university_name',
            y_column='estimated_total_annual_cost',
            graph_type='bar'
        )
        
        return {
            'cost_data': cost_data,
            'visualization': graph
        }
```

## Website UI Enhancements

### Add Graph Container
```html
<!-- In Website index.html -->
<div class="tile" id="visualization-tile">
  <h2>Visual Analysis</h2>
  <div id="graph-container">
    <!-- Plotly graphs injected here -->
  </div>
  <button onclick="exportGraph()">Export as PNG</button>
</div>
```

### CSS Styling
```css
#visualization-tile {
  grid-area: viz;
  min-height: 400px;
}

#graph-container {
  width: 100%;
  height: 100%;
  overflow-y: auto;
}

.plotly-graph {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
```

## Example Conversation Flow

```
User: "I'm deciding between MIT and Berkeley for a master's in CS. 
       Show me the full financial picture."

Claude:
  [calls university-cost MCP for MIT master]
  [calls university-cost MCP for Berkeley master]
  
  → MIT: $78,364/year total
  → Berkeley: $70,000/year total
  
  [calls graph-generation MCP]
  generate_comparison_chart({
    data: [
      {uni: 'MIT', tuition: 59750, housing: 12680, living: 5540},
      {uni: 'Berkeley', tuition: 45000, housing: 18000, living: 7000}
    ],
    category_column: 'uni',
    value_columns: ['tuition', 'housing', 'living']
  })
  
Response:
  "Here's the cost comparison:
  
  MIT Total: $78,364/year
  Berkeley Total: $70,000/year
  
  [Interactive grouped bar chart appears showing breakdown]
  
  Berkeley is ~$8,400/year cheaper, saving you $16,800 over a 
  2-year master's program. However, MIT has a 4% acceptance rate 
  vs Berkeley's 15%, and MIT graduates average $10k higher starting salaries.
  
  Would you like me to show the 30-year ROI projection for both?"
```

## Performance Considerations

### Graph Generation Speed
- **Simple charts** (bar, line): 50-200ms
- **Complex** (heatmap, multi-series): 200-500ms
- **Large datasets** (1000+ points): 500ms-2s

### Optimization Strategies
1. **Cache generated graphs** by data hash
2. **Lazy load Plotly.js** (CDN ~3MB)
3. **Downsample** large datasets before sending to client
4. **Server-side rendering** for initial load

### Response Size
- HTML output: 50-500KB (includes Plotly.js CDN link)
- JSON figure: 10-100KB (for client-side rendering)
- Static image: 100-500KB (PNG export)

## Testing Integration

### End-to-End Test
```bash
# Terminal 1: Start Website
cd Website && npm run dev

# Terminal 2: Start University Cost MCP
cd university-cost-mcp && python server/mcp_server.py

# Terminal 3: Start Graph Generation MCP
cd graph-generation-mcp && python server/mcp_server.py

# Terminal 4: Test query
python test_integration.py
```

### Test Script
```python
# test_integration.py
async def test_full_pipeline():
    # 1. Get university data
    mit_data = await univ_mcp.call_tool('get_university_cost', {
        'university_name': 'MIT',
        'degree_level': 'master'
    })
    
    # 2. Generate graph
    graph = await graph_mcp.call_tool('generate_bar_chart', {
        'data': [mit_data],
        'x_column': 'university_name',
        'y_column': 'estimated_total_annual_cost',
        'title': 'MIT Master Program Cost'
    })
    
    # 3. Verify output
    assert 'html' in graph
    assert 'figure' in graph
    assert graph['type'] == 'bar'
    
    print("✅ Integration test passed!")
```

## Future Enhancements

### Phase 2: Advanced Visualizations
- [ ] Animated transitions between graphs
- [ ] 3D scatter plots for multi-variable analysis
- [ ] Interactive sliders for "what-if" scenarios
- [ ] Real-time graph updates as user changes inputs

### Phase 3: Dashboard
- [ ] Multi-graph dashboard view
- [ ] Custom graph templates
- [ ] Export to PDF report with all graphs
- [ ] Shareable graph URLs

### Phase 4: AI-Enhanced
- [ ] Natural language query to graph generation
- [ ] Automatic insight annotations on graphs
- [ ] Trend detection and forecasting overlays
- [ ] Comparative analysis suggestions

---

**Integration Status**: Architecture Complete, Implementation Ready  
**Recommended Start**: Method 1 (Claude Desktop Orchestration)  
**Next Milestone**: Website UI enhancement for graph embedding
