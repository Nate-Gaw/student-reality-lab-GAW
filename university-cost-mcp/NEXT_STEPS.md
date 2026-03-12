# University Cost MCP - Next Steps

## Immediate Actions (Do This Now)

### 1. Install Dependencies
```bash
cd "D:/College Classes/IS219/student-reality-lab-GAW/university-cost-mcp"
pip install -r requirements.txt
```

This will install:
- `mcp` - Model Context Protocol library
- `sqlalchemy` - Database ORM
- `beautifulsoup4` - Web scraping
- `requests` - HTTP client
- `pydantic` - Data validation
- And 15 other dependencies

**Installation time**: ~2-3 minutes

### 2. Initialize Database
```bash
python setup_db.py
```

This will:
- Create `universities.db` SQLite database
- Create all tables
- Load 10 sample universities
- Output: "✓ Setup complete!"

**Execution time**: ~5 seconds

### 3. Test the System
```bash
python test_client.py
```

This will:
- Start the MCP server
- Test all 6 tools
- Validate responses
- Show example queries

**Expected output**: "✅ All tests completed!"

### 4. (Optional) Configure for Production
```bash
cp .env.example .env
# Edit .env and set:
DATABASE_URL=postgresql://user:pass@localhost:5432/university_costs
OPENAI_API_KEY=sk-...  # For LLM-enhanced scraping (Phase 2)
```

---

## Integration Options

### Option A: Use with Claude Desktop (Recommended)

1. **Find your Claude config file**:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`

2. **Add this MCP server**:
   ```json
   {
     "mcpServers": {
       "university-cost": {
         "command": "python",
         "args": [
           "D:/College Classes/IS219/student-reality-lab-GAW/university-cost-mcp/server/mcp_server.py"
         ]
       }
     }
   }
   ```

3. **Restart Claude Desktop**

4. **Test with a query**:
   ```
   "What's the tuition cost at MIT for a master's degree?"
   ```

   Claude will automatically use the MCP tool to fetch real data!

### Option B: Integrate with Your Website

See [INTEGRATION.md](INTEGRATION.md) for three integration methods:
1. **MCP Tool Access** - Claude coordinates both systems
2. **API Bridge** - Create REST API wrapper (FastAPI)
3. **Shared Database** - Direct SQL queries from Website

**Recommended for now**: Option 1 (MCP Tool Access via Claude)

### Option C: Use Standalone (Python Scripts)

```python
from data.storage.database import DatabaseManager
from server.query_handler import QueryHandler

db = DatabaseManager()
handler = QueryHandler(db)

# Get university cost
result = handler.get_university_cost(
    university_name="MIT",
    degree_level="master",
    student_type="international"
)
print(result)
```

---

## Phase 2 Expansion (Next Steps)

### Sprint 11: Data Expansion
1. **Batch fetch US universities**: Use College Scorecard to load 500+ US schools
2. **Currency conversion**: Integrate exchange rate API
3. **UK data**: Integrate UK HESA API (if key available)
4. **Scheduled updates**: Add cron job for nightly refresh

### Sprint 12: Website Integration
1. **Create API bridge**: FastAPI wrapper for REST access
2. **Add university selector**: UI component in Website
3. **Real-time calculations**: Update projections with real costs
4. **Enhanced ROI**: Factor in scholarships, placement rates

### Sprint 13: Advanced Features
1. **LLM-enhanced scraping**: Use GPT-4 for intelligent extraction
2. **Scholarship matching**: Integrate financial aid data
3. **Cost predictions**: ML model for future cost trends
4. **Mobile optimization**: Responsive design improvements

---

## Troubleshooting

### Issue: "Import 'mcp' could not be resolved"
**Solution**: Run `pip install -r requirements.txt`

### Issue: "Database locked"
**Solution**: Close any other processes using the database
```bash
# Find processes
lsof universities.db  # Mac/Linux
# Or just restart your terminal
```

### Issue: "Could not find cost data for [university]"
**Solution**: The university isn't in the database yet. Options:
1. Add it to `sample_data/universities.json` and re-run setup
2. Let the web scraper fetch it (if website URL known)
3. Query a similar university first to test functionality

### Issue: MCP server not connecting in Claude
**Solution**:
1. Check config file path is absolute
2. Verify Python in PATH: `which python` or `where python`
3. Check server stderr: Look for error messages
4. Restart Claude Desktop

---

## Understanding the System

### Data Flow Overview
```
User Query (via Claude)
    ↓
MCP Server receives tool call
    ↓
Query Handler checks cache
    ↓
[If cached & fresh] → Return data
[If missing/stale] → Acquire from source
    ↓
Normalize data to schema
    ↓
Store in database
    ↓
Format response
    ↓
Return to user
```

### Current Data Sources
1. **US College Scorecard** (active) - 100+ US universities
2. **Sample Data** (active) - 10 international universities
3. **Web Scraper** (ready) - Any university website
4. **International APIs** (planned) - UK, Canada, Australia, etc.

### Cost Components Tracked
- Tuition (domestic & international)
- Application fees
- Housing costs
- Living expenses
- Student fees
- Books/supplies
- Health insurance
- **Total**: Estimated annual cost

### Additional Data
- Acceptance rates
- Graduation rates
- Enrollment counts
- Scholarship availability
- Financial aid availability
- Official website URLs
- Data quality scores

---

## Performance Expectations

### Response Times
- **Cached data**: 50-100ms
- **First-time API fetch**: 2-5 seconds
- **Web scraping**: 3-10 seconds per university

### Data Freshness
- **TTL**: 90 days
- **Refresh trigger**: Automatic on query if stale
- **Update frequency**: Manual (scheduled updates in Phase 2)

### Coverage (Current)
- **US**: 100+ universities (via API)
- **International**: 10 sample universities
- **Total**: ~110 universities

### Coverage (Phase 2 Target)
- **US**: 500+ universities
- **UK**: 100+ universities
- **Global**: 50+ top universities
- **Total**: 650+ universities

### Coverage (Phase 3 Vision)
- **Global**: 5,000+ universities across 50+ countries

---

## File Reference

### Essential Files
- `setup_db.py` - **Run this first** to initialize database
- `test_client.py` - Test all MCP tools
- `server/mcp_server.py` - Main MCP server (run for standalone mode)

### Configuration
- `.env` - Environment variables (API keys, DB URL)
- `config/sources.json` - Data source registry

### Documentation
- `README.md` - Overview and quick start
- `QUICKSTART.md` - Step-by-step setup guide
- `ARCHITECTURE.md` - Detailed system design (500+ lines)
- `INTEGRATION.md` - Website integration guide
- `IMPLEMENTATION_SUMMARY.md` - What was built

### Data
- `sample_data/universities.json` - 10 sample universities
- `universities.db` - SQLite database (created after setup)

---

## Support & Resources

### Project Documentation
- Main README: `/university-cost-mcp/README.md`
- Architecture: `/university-cost-mcp/ARCHITECTURE.md`
- Integration: `/university-cost-mcp/INTEGRATION.md`
- Sprint Log: `/sprints/sprint-10-2026-03-09-university-cost-mcp-foundation.md`

### Learning Resources
- MCP Documentation: https://modelcontextprotocol.io
- SQLAlchemy Docs: https://docs.sqlalchemy.org
- College Scorecard API: https://collegescorecard.ed.gov/data/documentation/

### Need Help?
1. Check `ARCHITECTURE.md` for detailed explanations
2. Review `test_client.py` for usage examples
3. Read error messages carefully (they're descriptive!)
4. Check the sprint log for implementation details

---

## Success Checklist

Before considering Phase 1 complete:

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database initialized (`python setup_db.py`)
- [ ] Tests passing (`python test_client.py`)
- [ ] MCP server runs without errors (`python server/mcp_server.py`)
- [ ] Sample query works (test with MIT, Oxford, or TUM)
- [ ] (Optional) Claude Desktop integration configured

Once all checked, you're ready for:
- Real-world queries
- Website integration planning
- Phase 2 data expansion

---

**Quick Start Time**: 5-10 minutes  
**Full Setup Time**: 15-20 minutes (including Claude integration)  
**Ready for Production**: Phase 1 complete, Phase 2 recommended for expansion
