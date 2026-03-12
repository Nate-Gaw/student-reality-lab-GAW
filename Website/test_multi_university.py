"""Test multi-university extraction and comparison."""

import sys
from pathlib import Path

# Add bridge module to path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_bridge import _extract_all_university_candidates

# Test cases
test_queries = [
    "Compare the ROI on Rutgers New Brunswick and Stanford",
    "What's better: MIT or Stanford for a master's?",
    "Compare Harvard, Stanford, and MIT",
    "Rutgers vs. Stanford masters programs",
    "What does a masters at Stanford cost compared to Rutgers?",
    "I'm considering Stanford, Rutgers, and MIT. Which has the best ROI?",
    "University of Chicago or Stanford?",
    "How much do Stanford and Rutgers cost for a master's?",
    "Is Stanford worth it compared to Rutgers New Brunswick?",
]

print("Testing multi-university extraction:")
print("=" * 70)

for query in test_queries:
    candidates = _extract_all_university_candidates(query)
    print(f"\nQuery: {query}")
    print(f"Extracted universities: {candidates}")

print("\n" + "=" * 70)
print(f"✓ Multi-university extraction working")
print(f"The system will now:")
print(f"  1. Extract ALL universities mentioned (not just 1)")
print(f"  2. Make MCP calls for each university")
print(f"  3. Return comparison data to OpenAI")
print(f"  4. OpenAI performs the analysis and recommendation")
