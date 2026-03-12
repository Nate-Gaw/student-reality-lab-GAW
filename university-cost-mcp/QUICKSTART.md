# Quick Start Guide

## Installation

1. **Install dependencies**:
   ```bash
   cd university-cost-mcp
   pip install -r requirements.txt
   ```

2. **Configure environment** (optional for basic testing):
   ```bash
   cp .env.example .env
   # Edit .env if you want to add API keys for enhanced features
   ```

3. **Initialize database**:
   ```bash
   python setup_db.py
   ```

4. **Test the system**:
   ```bash
   python test_client.py
   ```

## Using the MCP Server

### Standalone Testing
```bash
python server/mcp_server.py
```

### Integration with Claude Desktop

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "university-cost": {
      "command": "python",
      "args": ["D:/path/to/university-cost-mcp/server/mcp_server.py"]
    }
  }
}
```

## Example Queries

Once integrated with Claude Desktop, you can ask:

- "What's the cost of attending MIT for a master's degree?"
- "Compare costs between MIT, Oxford, and TUM for bachelor's programs"
- "Show me universities in Germany"
- "What are the average tuition costs for bachelor's programs?"

## Available Tools

1. **get_university_cost** - Get detailed cost breakdown
2. **get_universities_by_country** - List universities by country
3. **compare_university_costs** - Compare multiple universities
4. **search_universities** - Search by name or location
5. **get_cost_statistics** - Statistical analysis

## Sample Data

The system comes pre-loaded with 10 sample universities from 9 countries:
- MIT (USA)
- Oxford (UK)
- Toronto (Canada)
- NUS (Singapore)
- TUM (Germany)
- Melbourne (Australia)
- ETH Zurich (Switzerland)
- Tokyo (Japan)

## Expanding the Database

### Option 1: Use College Scorecard API
The system automatically fetches US university data when queried.

### Option 2: Add Custom Data
Edit `sample_data/universities.json` and re-run `python setup_db.py`.

### Option 3: Web Scraping
The built-in web scraper can extract costs from university websites:

```python
from data.acquisition.web_scraper import UniversityWebScraper

scraper = UniversityWebScraper()
data = scraper.scrape_university("Stanford University", "https://www.stanford.edu")
```

## Troubleshooting

### "No module named 'mcp'"
```bash
pip install mcp
```

### "Database locked" error
Close any other processes using the database and try again.

### "Could not find cost data"
The university might not be in the database yet. The system will attempt to acquire data automatically when first queried.

## Next Steps

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system documentation.
