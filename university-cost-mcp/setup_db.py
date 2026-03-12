"""
Setup script to initialize the database and load sample data.
"""
import json
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

from data.storage.database import DatabaseManager
from datetime import datetime


def load_sample_data(db_manager: DatabaseManager):
    """Load sample university data into database."""
    sample_file = os.path.join(os.path.dirname(__file__), "sample_data", "universities.json")
    
    if not os.path.exists(sample_file):
        print(f"Sample data file not found: {sample_file}")
        return
    
    with open(sample_file, 'r', encoding='utf-8') as f:
        universities = json.load(f)
    
    print(f"Loading {len(universities)} sample universities...")
    
    for uni in universities:
        # Add timestamp and calculate total cost
        uni['last_updated'] = datetime.now()
        
        # Calculate estimated total
        costs = [
            uni.get('international_tuition', 0),
            uni.get('estimated_housing_cost', 0),
            uni.get('estimated_living_cost', 0),
            uni.get('student_fees', 0),
            uni.get('books_supplies', 0),
            uni.get('health_insurance', 0)
        ]
        uni['estimated_total_annual_cost'] = sum(c for c in costs if c)
        
        try:
            db_manager.add_university(uni)
            print(f"  ✓ {uni['university_name']} ({uni['degree_level']})")
        except Exception as e:
            print(f"  ✗ Error adding {uni['university_name']}: {e}")
    
    print("Sample data loaded successfully!")


def main():
    """Initialize database and load sample data."""
    print("=" * 60)
    print("University Cost MCP - Database Setup")
    print("=" * 60)
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    print("\n1. Creating database tables...")
    db_manager.create_tables()
    print("   ✓ Tables created")
    
    print("\n2. Loading sample data...")
    load_sample_data(db_manager)
    
    print("\n" + "=" * 60)
    print("Setup complete! You can now run the MCP server:")
    print("  python server/mcp_server.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
