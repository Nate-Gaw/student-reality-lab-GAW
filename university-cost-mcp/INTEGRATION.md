# University Cost MCP Integration Guide

## Overview

The University Cost MCP tool integrates with the existing Website financial advisor to provide real-world university cost data for more accurate ROI calculations.

## Architecture Integration

```
┌─────────────────────────────────────────────────────────┐
│                    User (Claude Desktop)                │
└─────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         │                                   │
         ▼                                   ▼
┌──────────────────┐              ┌────────────────────┐
│   Website UI     │              │ University Cost    │
│  (Financial      │              │    MCP Server      │
│   Advisor)       │◄─────────────┤                    │
│                  │   Cost Data  │ - API Sources      │
│ - OpenAI Chat    │              │ - Web Scraper      │
│ - Break-even     │              │ - Database Cache   │
│ - Projections    │              │                    │
└──────────────────┘              └────────────────────┘
         │                                   │
         └───────────────┬───────────────────┘
                         ▼
              ┌────────────────────┐
              │   PostgreSQL DB    │
              │ (Shared Storage)   │
              └────────────────────┘
```

## Use Cases

### 1. Enhanced User Queries
**Before**:
```
User: "Should I get a master's degree?"
Website: Uses hardcoded averages ($40k bachelor, $50k master)
```

**After**:
```
User: "Should I get a master's in CS from MIT?"
Claude: [queries university-cost MCP]
Website: Uses actual MIT costs ($57,590 bachelor, $59,750 master)
        + Boston living costs ($18,220/year)
        → Accurate break-even calculation
```

### 2. Multi-University Comparison
```
User: "Compare master's programs at MIT, Stanford, and Georgia Tech"
Claude: [calls compare_university_costs]
        Returns:
        - Georgia Tech: $33,020/year (rank 1)
        - MIT: $59,750/year (rank 2)
        - Stanford: $61,500/year (rank 3)
Website: Shows 30-year projections for all three
```

### 3. International Student Planning
```
User: "I'm from India. Where should I study CS?"
Claude: [queries by country, compares costs]
        - NUS Singapore: $17,550/year
        - TUM Germany: $144/year (!)
        - MIT USA: $57,590/year
Website: Factors in visa costs, exchange rates, scholarship data
```

## Integration Methods

### Method 1: Direct MCP Tool Access (Recommended)
Claude Desktop can call both systems simultaneously:

```javascript
// Website receives enhanced query
const prompt = `
  User wants to compare MIT master's vs bachelor's.
  University costs: ${mcp_data}
  
  Calculate break-even and 30-year advantage.
`;

const response = await openai.responses.create({
  model: 'gpt-4o-mini',
  input: prompt
});
```

### Method 2: API Bridge
Create a REST API wrapper around the MCP server:

```python
# api_bridge.py
from fastapi import FastAPI
from server.query_handler import QueryHandler

app = FastAPI()

@app.get("/api/university/{name}/cost")
def get_cost(name: str, degree: str):
    handler = QueryHandler(db_manager)
    return handler.get_university_cost(name, degree)
```

Then call from Website:
```javascript
const response = await fetch('http://localhost:8000/api/university/MIT/cost?degree=master');
const costData = await response.json();
```

### Method 3: Shared Database
Both systems write to/read from the same PostgreSQL database:

```javascript
// Website can query directly
const query = `
  SELECT international_tuition, estimated_housing_cost, estimated_living_cost
  FROM universities
  WHERE university_name ILIKE '%MIT%' AND degree_level = 'master'
`;
```

## Enhanced Website Features

### 1. Real University Mode
Add a toggle in the Website UI:

```html
<div class="scenario-source">
  <label>
    <input type="radio" name="source" value="defaults" checked>
    Use General Averages
  </label>
  <label>
    <input type="radio" name="source" value="real">
    Use Real University Data
  </label>
  <input type="text" id="university-name" placeholder="Enter university name" disabled>
</div>
```

When "Real" is selected:
1. User types university name
2. Website fetches costs via MCP
3. Updates bachelor/master values automatically
4. Recalculates all projections

### 2. University Recommendation
Website can suggest universities based on user's financial constraints:

```javascript
async function recommendUniversities(maxBudget, preferredDegree) {
  // Query MCP for universities under budget
  const universities = await mcpClient.call_tool('search_universities', {
    search_term: preferredDegree,
    limit: 50
  });
  
  const affordable = universities.filter(u => 
    u.estimated_total_annual_cost <= maxBudget
  );
  
  return affordable.sort((a, b) => 
    b.graduation_rate - a.graduation_rate
  );
}
```

### 3. Break-Even with Real Data
Enhanced calculation using MCP data:

```javascript
async function calculateBreakEvenWithRealData(universityName) {
  // Get costs from MCP
  const bachelor = await getCost(universityName, 'bachelor');
  const master = await getCost(universityName, 'master');
  
  // Calculate with real numbers
  const bachelorDebt = bachelor.costs.tuition * 4 + bachelor.costs.housing * 4;
  const masterDebt = bachelorDebt + (master.costs.tuition * 2 + master.costs.housing * 2);
  
  // Use acceptance rate for risk assessment
  const competitiveness = 1 / master.statistics.acceptance_rate;
  
  return {
    breakEvenYear,
    totalAdvantage,
    riskFactor: competitiveness
  };
}
```

## Data Flow Example

1. **User Query**:
   ```
   User: "Is MIT master's worth it compared to just bachelor's?"
   ```

2. **Claude calls MCP**:
   ```python
   mcp.call_tool('compare_university_costs', {
     university_names: ['MIT', 'MIT'],
     degree_level: 'bachelor',  # then 'master'
   })
   ```

3. **MCP checks cache**:
   - MIT bachelor: Found, 30 days old ✓
   - MIT master: Found, 30 days old ✓

4. **MCP returns**:
   ```json
   {
     "bachelor": {
       "tuition": 57590,
       "housing": 12680,
       "total": 76194
     },
     "master": {
       "tuition": 59750,
       "housing": 12680,
       "total": 78364
     }
   }
   ```

5. **Claude sends to Website**:
   ```javascript
   const scenario = {
     bachelorTuition: 57590,
     bachelorHousing: 12680,
     masterTuition: 59750,
     masterHousing: 12680,
     bachelorSalary: 95000,  // CS major average
     masterSalary: 125000    // CS master average
   };
   ```

6. **Website calculates**:
   - Bachelor total cost: $304,776 (4 years)
   - Master total cost: $461,464 (6 years)
   - Salary difference: $30,000/year
   - Break-even: Year 10 after bachelor
   - 30-year advantage: $780,000

7. **Response**:
   ```
   For MIT specifically, a master's degree breaks even in year 10
   and provides an estimated $780,000 advantage over 30 years.
   However, MIT's low acceptance rate (4%) means this specific
   path is highly competitive.
   ```

## Configuration

### Claude Desktop Config
```json
{
  "mcpServers": {
    "university-cost": {
      "command": "python",
      "args": ["D:/College Classes/IS219/student-reality-lab-GAW/university-cost-mcp/server/mcp_server.py"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost/university_costs"
      }
    }
  }
}
```

### Website .env Update
```bash
# Existing
VITE_OPENAI_API_KEY=sk-...

# New (optional, for direct API bridge access)
VITE_MCP_API_URL=http://localhost:8000
VITE_USE_REAL_DATA=true
```

## Performance Considerations

### Caching Strategy
```
User Query
  ↓
MCP Cache Check (90-day TTL)
  ↓ (if miss)
API Fetch (2-3s)
  ↓
Store in DB
  ↓
Return (future: instant)
```

### Response Time Targets
- **Cached data**: < 100ms
- **API fetch**: < 5s (first time only)
- **Website calculation**: < 200ms
- **Total user experience**: < 500ms (cached) or < 6s (fresh)

### Optimization Ideas
1. **Preload Popular Universities**: Pre-fetch top 100 universities on startup
2. **Predictive Caching**: When MIT bachelor is queried, also fetch MIT master
3. **Edge Caching**: Use CDN for frequently accessed universities
4. **Batch Queries**: Fetch multiple universities in parallel

## Future Enhancements

### Phase 1: Current ✅
- MCP server operational
- 10 sample universities
- 6 query tools
- Database caching

### Phase 2: Near-term
- [ ] API bridge for Website integration
- [ ] University selector UI in Website
- [ ] Real-time cost updates in projections
- [ ] Scholarship data integration

### Phase 3: Advanced
- [ ] Machine learning for cost predictions
- [ ] Alumni salary data integration
- [ ] Job placement rate factors
- [ ] ROI calculator with real employment stats
- [ ] Student loan interest rate integration

## ROI Calculation Enhancement

### Current Formula (Website)
```javascript
const advantage = (masterSalary - bachelorSalary) * years - debtDifference;
```

### Enhanced Formula (with MCP data)
```javascript
const advantage = (
  (masterSalary * employmentRate) - (bachelorSalary * bachelorEmploymentRate)
) * years 
  - debtDifference 
  - (loanInterest * debtDifference * loanTerm)
  + scholarshipAmount
  - costOfLivingAdjustment;
```

**New factors from MCP**:
- `employmentRate`: University-specific job placement
- `scholarshipAmount`: Average financial aid
- `costOfLivingAdjustment`: City-specific costs
- `loanInterest`: Current federal/private rates

## Security & Privacy

### Data Handling
- No personal data stored (anonymous query logs only)
- API keys encrypted in .env
- Database access restricted to localhost

### Rate Limiting
- Web scraping: 10 requests/minute per domain
- API calls: Respect source-specific limits
- MCP queries: Unlimited (cached data)

### Compliance
- robots.txt compliance for all scrapers
- Terms of service adherence for all APIs
- Data source attribution in responses

## Troubleshooting

### Common Issues

**1. MCP server not connecting**
```bash
# Check if server is running
ps aux | grep mcp_server.py

# Check logs
tail -f mcp_server.log
```

**2. Website not receiving MCP data**
- Verify Claude Desktop config path
- Restart Claude Desktop after config change
- Check MCP server stderr for errors

**3. Stale data returned**
```python
# Force refresh
db_manager.update_university(university_id, {'last_updated': datetime(2020, 1, 1)})
# Next query will trigger fresh fetch
```

## Testing Integration

### End-to-End Test
```bash
# Terminal 1: Start MCP server
cd university-cost-mcp
python server/mcp_server.py

# Terminal 2: Start Website
cd ../Website
npm run dev

# Terminal 3: Test query
python test_integration.py
```

### Test Script
```python
# test_integration.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_integration():
    # 1. Query MCP
    result = await mcp_client.call_tool('get_university_cost', {
        'university_name': 'MIT',
        'degree_level': 'master'
    })
    
    # 2. Verify response format
    assert 'costs' in result
    assert result['costs']['tuition'] > 0
    
    # 3. Simulate Website usage
    scenario = build_financial_scenario(result)
    assert scenario['masterTuition'] == result['costs']['tuition']
    
    print("✅ Integration test passed")

asyncio.run(test_integration())
```

---

**Last Updated**: March 9, 2026  
**Integration Status**: Architecture Complete, Implementation Phase 2 Ready  
**Next Milestone**: API bridge development for seamless Website integration
