"""Force add Stanford University data to the database."""

import json
from datetime import datetime
from pathlib import Path
from data.storage.database import DatabaseManager

# Initialize database
db = DatabaseManager("sqlite:///universities.db")
db.create_tables()

# Load Stanford data from sample file
sample_file = Path(__file__).parent / "sample_data" / "universities.json"
with open(sample_file, "r", encoding="utf-8") as f:
    universities = json.load(f)

stanford_entries = [u for u in universities if "Stanford" in u.get("university_name", "")]

print(f"Found {len(stanford_entries)} Stanford entries in sample data")

for uni in stanford_entries:
    uni["last_updated"] = datetime.now()
    costs = [
        uni.get("international_tuition", 0),
        uni.get("estimated_housing_cost", 0),
        uni.get("estimated_living_cost", 0),
        uni.get("student_fees", 0),
        uni.get("books_supplies", 0),
        uni.get("health_insurance", 0),
    ]
    uni["estimated_total_annual_cost"] = sum(float(c) for c in costs if c)
    
    print(f"\nAdding: {uni.get('university_name')} ({uni.get('degree_level')})")
    print(f"  Tuition: ${uni.get('international_tuition')}")
    print(f"  Total Annual Cost: ${uni.get('estimated_total_annual_cost')}")
    
    try:
        db.add_university(uni)
        print("  ✓ Successfully added")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

# Verify Stanford is in database
print("\n" + "="*50)
print("Verifying Stanford in database...")
results = db.search_universities("Stanford", limit=10)
print(f"Found {len(results)} Stanford entries in database:")
for r in results:
    print(f"  - {r.get('university_name')} ({r.get('degree_level')}): ${r.get('international_tuition')}")
