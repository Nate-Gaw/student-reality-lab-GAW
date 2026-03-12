# University Cost MCP - Architecture Documentation

## System Overview

The University Cost MCP is a Model Context Protocol server that aggregates global university cost data from multiple sources and provides a unified query interface. The system follows a modular pipeline architecture optimized for reliability, scalability, and data freshness.

## Architecture Components

### 1. MCP Interface Layer
**File**: `server/mcp_server.py`

The MCP server exposes standardized tools for querying university cost information:

- `get_university_cost` - Get detailed cost breakdown for a specific university
- `get_universities_by_country` - List all universities in a country
- `compare_university_costs` - Compare costs across multiple institutions
- `search_universities` - Search by name, location, or program
- `get_cost_statistics` - Statistical analysis of costs by region/program

All tools follow the MCP specification for tool definitions and response formats.

### 2. Query Handler
**File**: `server/query_handler.py`

The query handler orchestrates the data pipeline:

```
User Query → Check Cache → Return Fresh Data
                ↓ (if stale/missing)
            Trigger Acquisition → Normalize → Store → Return
```

**Key Features**:
- Cache-first strategy (90-day TTL)
- Automatic fallback to data acquisition
- Priority-based source selection (APIs > Datasets > Scraping)
- Intelligent cost comparison and ranking

### 3. Data Storage Layer
**File**: `data/storage/database.py`

SQLAlchemy-based database layer supporting both SQLite (dev) and PostgreSQL (production).

**Schema** (`University` table):
- Identification: name, country, city
- Program: degree level, program name, available majors
- Costs: tuition (domestic/international), housing, living, fees
- Financial aid: scholarships, aid availability
- Statistics: acceptance rate, graduation rate, enrollment
- Metadata: data source, quality score, last updated

**Key Operations**:
- `add_university()` - Insert new record
- `get_university_by_name()` - Retrieve by name + degree level
- `get_universities_by_country()` - Country-based filtering
- `search_universities()` - Full-text search
- `get_stale_records()` - Find outdated records for refresh

### 4. Data Acquisition Layer

#### 4.1 API Sources
**File**: `data/acquisition/api_sources.py`

Integrates with government and education APIs:

**Implemented**:
- `CollegeScorecard` - US Department of Education (100+ institutions)
  - Endpoint: `https://api.data.gov/ed/collegescorecard/v1/schools`
  - Coverage: All US colleges and universities
  - Data: Tuition, housing, acceptance rates, graduation rates

**Planned**:
- `TimesHigherEducation` - Global rankings (requires key)
- `OpenDataPortal` - Government portals (UK, Canada, Australia, EU)

**Features**:
- Automatic response normalization
- Rate limiting with exponential backoff
- Error handling and retry logic

#### 4.2 Web Scraper
**File**: `data/acquisition/web_scraper.py`

Intelligent web scraping for data not available via APIs:

**Capabilities**:
- Automatic tuition page discovery from university homepage
- Regex-based cost extraction (tuition, housing, application fees)
- Rate-limited requests (2-3 second delay)
- Respectful crawling with proper User-Agent

**Planned Enhancement**: `LLMEnhancedScraper`
- Use GPT-4 for intelligent extraction from complex layouts
- Handle PDFs and unstructured documents
- Adaptive parsing for varying website structures

### 5. Data Normalization Layer
**File**: `data/normalization/schema.py`

Pydantic models ensure data consistency:

```python
class UniversityCost(BaseModel):
    university_name: str
    country: str
    degree_level: DegreeLevel  # Enum: bachelor, master, doctoral
    currency: Currency  # Enum: USD, EUR, GBP, etc.
    domestic_tuition: Optional[float]
    international_tuition: Optional[float]
    # ... 20+ standardized fields
    data_quality_score: float  # 0.0-1.0 based on completeness
```

**Validation**:
- Type checking with Pydantic
- Enum constraints for categorical fields
- Optional fields for incomplete data sources
- Automatic timestamp generation

## Data Flow

### Query Flow (Cache Hit)
```
User → MCP Server → Query Handler → Database → Format Response → User
                                        ↓
                                  (< 90 days old)
```

### Query Flow (Cache Miss)
```
User → MCP Server → Query Handler → Database (empty/stale)
                                        ↓
                                  Data Acquisition:
                                    1. Try APIs (priority 1)
                                    2. Try datasets (priority 2)
                                    3. Try scraping (priority 3)
                                        ↓
                                  Normalize Data
                                        ↓
                                  Store in Database
                                        ↓
                                  Format Response → User
```

### Batch Update Flow
```
Scheduled Job → Get Stale Records → Batch Acquisition → Update Database
```

## Configuration

### Environment Variables (.env)
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/university_costs
OPENAI_API_KEY=sk-...  # For LLM-enhanced scraping
ANTHROPIC_API_KEY=sk-ant-...  # Alternative LLM
```

### Data Sources (config/sources.json)
```json
{
  "data_sources": [
    {
      "source_name": "US College Scorecard",
      "priority": 1,
      "reliability_score": 0.95
    }
  ],
  "cache_ttl_days": 90
}
```

## Scalability Considerations

### Current Implementation
- **Storage**: SQLite (dev) / PostgreSQL (prod)
- **Caching**: Database-backed with timestamp checks
- **Rate Limiting**: Per-source delays (2-3 seconds)
- **Coverage**: 100+ US universities + 10 sample international

### Future Enhancements
1. **Redis Cache**: Add memory cache layer for frequently accessed universities
2. **Async Processing**: Use Celery/RQ for background data acquisition
3. **CDN Integration**: Cache formatted responses at edge
4. **Elasticsearch**: Full-text search with fuzzy matching
5. **API Gateway**: Rate limiting and authentication for external access
6. **Monitoring**: DataDog/Prometheus for data freshness metrics

## Data Quality Management

### Quality Score Calculation
```python
score = (filled_required_fields / total_required_fields) * 
        source_reliability_score
```

**Required Fields**:
- university_name, country, degree_level (100% required)
- tuition (international or domestic) (80% weight)
- Official website URL (50% weight)

### Staleness Detection
- Records > 90 days old marked for refresh
- Batch update job runs nightly (planned)
- Priority refresh for frequently queried universities

## Testing

### Unit Tests (Planned)
- Database CRUD operations
- API response normalization
- Cost calculation accuracy
- Schema validation

### Integration Tests
- End-to-end query flow
- Data acquisition pipeline
- Multi-source fallback logic

### Test Client
**File**: `test_client.py`

Comprehensive MCP tool testing:
```bash
python test_client.py
```

Tests all 6 tools with sample data and validates response formats.

## Deployment

### Local Development
```bash
# Setup
python setup_db.py

# Run server
python server/mcp_server.py

# Test
python test_client.py
```

### MCP Integration (Claude Desktop)
Add to `claude_desktop_config.json`:
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

### Production Deployment
1. **Database**: PostgreSQL with connection pooling
2. **Process Manager**: systemd or pm2 for server uptime
3. **Reverse Proxy**: nginx for external API access
4. **Monitoring**: Log aggregation and alerting
5. **Backup**: Daily database snapshots

## Future Roadmap

### Phase 1 (Current) ✅
- Core MCP server with 6 tools
- SQLite database
- US College Scorecard integration
- Basic web scraping
- Sample data (10 universities)

### Phase 2 (Next)
- [ ] Additional API integrations (UK HESA, Universities Canada)
- [ ] LLM-enhanced web scraping
- [ ] Scheduled data refresh system
- [ ] Expand to 500+ universities
- [ ] Cost currency conversion

### Phase 3 (Future)
- [ ] Real-time data updates
- [ ] User authentication and rate limiting
- [ ] Custom program cost estimation
- [ ] Scholarship matching system
- [ ] Mobile API with REST endpoints
- [ ] Geographic cost-of-living adjustments
- [ ] Visa and immigration cost inclusion

## Error Handling

### API Failures
- Retry with exponential backoff (3 attempts)
- Fallback to next priority source
- Return partial data with quality score

### Database Errors
- Connection pooling with automatic retry
- Transaction rollback on constraint violations
- Graceful degradation (return cached even if stale)

### Scraping Errors
- Timeout handling (15 second limit)
- Rate limit detection and backoff
- Malformed HTML graceful parsing

## Performance Metrics

### Target SLAs
- Query response time: < 500ms (cached), < 5s (fresh acquisition)
- Data freshness: 90% of records < 90 days old
- API uptime: 99.5%
- Scraping success rate: > 70%

### Current Performance
- Sample data queries: ~50ms
- Database insert: ~10ms per record
- College Scorecard fetch: ~2-3s for 100 records

## Security Considerations

1. **API Keys**: Stored in .env, never committed
2. **Rate Limiting**: Respect source TOS
3. **Web Scraping**: robots.txt compliance
4. **Database**: SQL injection prevention via ORM
5. **Input Validation**: Pydantic schema validation
6. **HTTPS**: All external API calls over TLS

## License and Usage

### Data Sources
Each source has its own license and usage restrictions. Check individual source documentation before commercial use.

### Server Code
MIT License - free for academic and commercial use with attribution.

---

**Last Updated**: March 9, 2026  
**Version**: 1.0.0  
**Maintainer**: Student Reality Lab
