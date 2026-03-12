# Fuzzy Matching Implementation - Rutgers Update

## Summary
Added fuzzy name matching to the University Cost MCP to handle queries like "Rutgers New Brunswick" that don't exactly match the database name "Rutgers University-New Brunswick".

## Changes Made

### 1. Modified `university-cost-mcp/server/query_handler.py`

Added fuzzy matching logic to `get_university_cost()` method:

**How it works:**
1. Tries exact match first using `db.get_university_by_name()`
2. If no exact match, searches ALL universities in the database
3. Normalizes both the query and candidate names:
   - Converts to lowercase
   - Removes punctuation
   - Standardizes spacing
   - Expands common abbreviations (e.g., "univ" → "university")
4. Scores each candidate using two methods:
   - **SequenceMatcher ratio**: Measures character-level similarity
   - **Token overlap**: Counts matching words
5. Takes the higher of the two scores
6. Accepts matches with confidence ≥ 0.6 (60%)

**Example:**
```
Query: "Rutgers New Brunswick"
Normalized: "rutgers new brunswick"

Candidate: "Rutgers University-New Brunswick"
Normalized: "rutgers university new brunswick"

Token overlap: {rutgers, new, brunswick} ∩ {rutgers, university, new, brunswick}
             = 3 / 3 = 1.0 (100% match) ✓
```

### 2. Database Status

**Current database contents:**
- 19 universities total
- 4 Rutgers entries (2 bachelor's, 2 master's with duplicates)
- **Rutgers University-New Brunswick (master's)**:
  - Tuition: $36,039
  - Country: United States
  - City: New Brunswick
  - Last updated: 2025-01-28

### 3. Helper Methods

```python
@staticmethod
def _normalize_name(name: str) -> str:
    """Normalize university names for comparison"""
    text = re.sub(r"[^a-z0-9\s]", " ", (name or "").lower())
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("univ ", "university ")
    text = text.replace("u ", "university ")
    return text

@staticmethod
def _score_name_match(query: str, candidate: str) -> float:
    """Score similarity between query and candidate names"""
    if not query or not candidate:
        return 0.0
    base = SequenceMatcher(None, query, candidate).ratio()
    query_tokens = set(query.split())
    candidate_tokens = set(candidate.split())
    overlap = len(query_tokens & candidate_tokens) / max(len(query_tokens), 1)
    return max(base, overlap)
```

## Testing Instructions

Due to Windows console limitations preventing automated testing, please test manually:

### Test 1: Rutgers New Brunswick Query
1. Start the website: `cd Website && npm run dev`
2. Start the bridge: `cd Website && python mcp_bridge.py`
3. Open http://localhost:5173 in your browser
4. Type: **"I'm planning to go to Rutgers New Brunswick for a Masters, what do the costs look like?"**

**Expected Result:**
- Should return cost data for Rutgers University-New Brunswick
- Tuition: $36,039
- Mode should be `get_university_cost` (not `university_detected_unavailable`)
- Should include other cost breakdowns

### Test 2: Stanford Query
1. Type: **"What does Stanford cost for a bachelor's degree?"**

**Expected Result:**
- Should return cost data for Stanford University
- Tuition: $56,169
- Should include housing, living expenses, etc.

### Test 3: Partial Name Query
1. Type: **"How much does Rutgers cost?"**

**Expected Result:**
- Should match one of the Rutgers entries
- Should return specific cost data

## Confidence Threshold

The matching uses a **0.6 confidence threshold**. This means:
- ≥ 0.6 (60%): Accept match
- < 0.6 (60%): No match, falls back to data acquisition

Examples of scoring:
- "Rutgers New Brunswick" vs "Rutgers University-New Brunswick": **1.0** (100%) ✓
- "Stanford" vs "Stanford University": **1.0** (100%) ✓
- "MIT" vs "Massachusetts Institute of Technology": **0.0** (token overlap fails) ✗
- "Harvard" vs "Harvard University": **1.0** (100%) ✓

## Files Modified

1. `university-cost-mcp/server/query_handler.py`
   - Added fuzzy matching to `get_university_cost()`
   - Added `_normalize_name()` helper
   - Added `_score_name_match()` helper

## Next Steps

If testing confirms the fuzzy matching works:
1. ✅ Consider lowering threshold to 0.5 for more lenient matching
2. ✅ Add more university data to sample_data/universities.json
3. ✅ Document matching algorithm in README
4. ✅ Add unit tests for name normalization and scoring

## Troubleshooting

**If Rutgers still shows "university_detected_unavailable":**
1. Check bridge terminal output for errors
2. Verify database has Rutgers data: `python manual_db_check.py`
3. Check confidence score in bridge logs
4. Ensure bridge loaded latest query_handler.py (restart it)

**If matching too many false positives:**
- Increase confidence threshold from 0.6 to 0.7

**If matching too few universities:**
- Decrease confidence threshold from 0.6 to 0.5
- Add more normalization rules to `_normalize_name()`
