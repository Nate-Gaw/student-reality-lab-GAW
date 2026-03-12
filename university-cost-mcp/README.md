# University Cost MCP Tool

A Model Context Protocol (MCP) server that aggregates and serves structured data about universities worldwide, including tuition costs, living expenses, and program information.

## Architecture

```
university-cost-mcp/
├── server/
│   ├── mcp_server.py          # Main MCP server
│   ├── query_handler.py       # Query routing and response
│   └── tools.py               # MCP tool definitions
├── data/
│   ├── acquisition/
│   │   ├── api_sources.py     # Government/education APIs
│   │   ├── web_scraper.py     # University website scraping
│   │   └── dataset_loader.py  # Load existing datasets
│   ├── normalization/
│   │   ├── schema.py          # Data schema definitions
│   │   └── normalizer.py      # Data transformation
│   └── storage/
│       ├── database.py        # Database interface
│       └── cache.py           # Query caching
├── config/
│   ├── database_config.py
│   └── sources.json           # API endpoints, data sources
├── sample_data/
│   └── universities.json      # Sample dataset for testing
└── requirements.txt

## Features

- Query university costs by name, country, or program
- Compare costs across multiple institutions
- Automatic data acquisition from multiple sources
- Intelligent extraction from unstructured data
- Periodic data refresh system

## Setup

```bash
cd university-cost-mcp
pip install -r requirements.txt
python setup_db.py
python server/mcp_server.py
```

## Usage

The MCP server exposes these tools:
- `get_university_cost` - Get detailed cost breakdown for a university
- `get_universities_by_country` - List universities in a specific country
- `compare_university_costs` - Compare costs across multiple universities
- `search_universities` - Search by name, location, or program

## Data Sources Priority

1. Government education statistics (primary)
2. International university registries
3. Official university websites (scraping fallback)
