import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from database import init_db, get_session
from query_handler import QueryHandler

# Initialize database
init_db()
session = get_session()
handler = QueryHandler(session)

# Test Rutgers New Brunswick
print("Testing: 'Rutgers New Brunswick' for master's degree")
print("-" * 50)
result = handler.get_university_cost("Rutgers New Brunswick", "master")
print(f"Result: {result}")
print()

# Test Stanford
print("Testing: 'Stanford' for bachelor's degree")
print("-" * 50)
result = handler.get_university_cost("Stanford", "bachelor")
print(f"Result: {result}")
