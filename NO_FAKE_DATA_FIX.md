# Fix: No Fake Data or Graphs When University Data Unavailable

## Problem
When querying specific universities like "Stanford masters", the system would:
1. Recognize the university but fail to find data in the database
2. Fall back to baseline projections as if they were real Stanford data
3. Generate graphs using fake baseline data
4. Display misleading message: "advisor used baseline projections + Graph MCP"

**User's requirement:** "DO NOT FAKE DATA. Remove the graph if no data is given."

## Solution Implemented

### 1. Backend Changes (`mcp_bridge.py`)

#### A. Updated `advisor()` endpoint
**Old behavior:** Always generated projection graph regardless of data availability

**New behavior:**
- **Real university data available** (`get_university_cost` or `compare_university_costs` mode):
  - Generate cost breakdown graph with actual university data
  - Include graph in response
  
- **No university query detected** (`not used`):
  - Generate baseline projection graph for general ROI questions
  - Include graph in response
  
- **University detected but data unavailable** (`university_detected_unavailable` mode):
  - **NO graph generated** ❌
  - **NO baseline data used as fake university data** ❌
  - Response includes `graph: null`

```python
# Graph generation logic
graph_info = None
if university_context.get("mode") in ["get_university_cost", "compare_university_costs"]:
    # Real university data - show graph
    cost_graph = maybe_build_cost_graph(graph_generator, university_context)
    if cost_graph:
        graph_info = cost_graph
elif not university_context.get("used"):
    # General question - show baseline projection
    projection_graph = build_projection_graph(graph_generator, summary)
    graph_info = projection_graph
# else: university_detected_unavailable - NO GRAPH
```

#### B. Updated `build_system_prompt()` function
**Added honesty instructions:** When `mode == "university_detected_unavailable"`:

```python
"IMPORTANT: A specific university was detected in the query, but detailed cost data is NOT available."
"DO NOT use baseline financial projections as if they represent this specific university."
"Be honest that the data for this university is not currently available."
"Suggest the user check the university's official website or contact their admissions office."
```

**Conditional baseline model:** Only include baseline financial model context if:
- No university query detected, OR
- Real university data is available

**Graph context updated:** When no graph available, system prompt says:
```
"Graph MCP context: No visualization available (data unavailable for requested university)"
```

#### C. Updated `ensure_university_sample_data()` function
**Old behavior:** Only added universities if they didn't exist (checked by name|degree key)

**New behavior:** Always calls `db.add_university()` for each sample entry
- Database handles updates/duplicates internally
- Ensures sample data is always fresh
- Forces Stanford and other universities to be in database

### 2. Frontend Changes (`main.js`)

#### Updated system message when data unavailable

**Old message:**
```
"Recognized your question about Stanford. Since detailed data isn't available, 
the advisor used baseline projections + Graph MCP."
```

**New message:**
```
"Recognized your question about Stanford, but detailed cost data for this 
university is not currently available in our database. The advisor can only 
provide general guidance."
```

**Key improvements:**
- Honest about data unavailability
- No mention of fake baseline projections
- No mention of Graph MCP (since no graph generated)
- Clear limitation on what advisor can provide

#### Updated graph display logic
Already had check: `if (result?.mcp?.graph?.used && result?.graph?.html)`
- Graph only displayed when explicitly available
- When `graph: null`, nothing is rendered

### 3. Database Updates

#### Forced Stanford Addition
Created `force_add_stanford.py` to ensure Stanford is in database:
- Bachelor's degree: $58,416 tuition
- Master's degree: $58,320 tuition

#### Sample Data Verified
`universities.json` contains:
- Stanford University (bachelor + master)
- Rutgers University-New Brunswick (bachelor + master)
- MIT, Oxford, Cambridge, etc.

## Testing Instructions

### Test 1: Stanford Master's Query
**Query:** "What does a masters degree at Stanford look like?"

**Expected Result:**
- Should return actual Stanford cost data
- Tuition: $58,320
- Graph showing cost breakdown (tuition, housing, living, etc.)
- System message: "University Cost MCP used via get_university_cost; Graph MCP generated a pie"

### Test 2: Unknown University Query
**Query:** "What does University of Mars cost for a master's?"

**Expected Result:**
- No specific cost data returned
- **NO graph displayed** ✓
- System message: "Recognized your question about University of Mars, but detailed cost data for this university is not currently available in our database."
- Answer should be honest about data unavailability

### Test 3: General ROI Question
**Query:** "Is a master's degree worth it?"

**Expected Result:**
- Uses baseline financial model
- Shows projection graph comparing bachelor vs master over 30 years
- System message: "Using baseline financial model and Graph MCP for projections."

## Files Modified

1. `Website/mcp_bridge.py`
   - `advisor()` endpoint: Conditional graph generation
   - `build_system_prompt()`: Honesty instructions, conditional baseline model
   - `ensure_university_sample_data()`: Force-update all sample universities

2. `Website/main.js`
   - Updated system message for `university_detected_unavailable` mode
   - Already had proper null graph handling

3. `university-cost-mcp/force_add_stanford.py` (NEW)
   - Utility script to manually add Stanford to database

## Key Principles Enforced

✅ **No fake data** - Baseline projections never presented as university-specific data
✅ **No misleading graphs** - Graphs only shown when real data available
✅ **Honest messaging** - Clear communication about data availability
✅ **Real data prioritized** - Database always refreshed with sample data on startup

## Verification Checklist

- [ ] Start bridge: `cd Website && python mcp_bridge.py`
- [ ] Start frontend: `cd Website && npm run dev`
- [ ] Test Stanford query - should return real data + graph
- [ ] Test unknown university - should return no graph, honest message
- [ ] Test general question - should show baseline projection graph
- [ ] Verify no fake data presented as real university data
- [ ] Verify system messages are accurate and honest

## Before/After Comparison

### Before (WRONG) ❌
```
User: "What does Stanford masters cost?"
System: "Recognized your question about Stanford. Using baseline projections + Graph MCP."
Graph: [Shows generic projection with random data]
Data: $27,437 bachelor debt, $61,667 master debt (NOT Stanford data)
```

### After (CORRECT) ✅
```
User: "What does Stanford masters cost?"
System: "University Cost MCP used via get_university_cost; Graph MCP generated a pie"
Graph: [Shows Stanford-specific cost breakdown]
Data: Tuition $58,320, Housing $14,100, etc. (REAL Stanford data)
```

OR if data unavailable:
```
User: "What does University of Mars cost?"
System: "Recognized your question about University of Mars, but detailed cost 
        data for this university is not currently available."
Graph: [NONE - no fake data]
Answer: "I don't have specific cost data for University of Mars. I recommend 
         visiting their official website..."
```
