import sys
sys.path.insert(0, '../university-cost-mcp')

from data.storage.database import DatabaseManager

db = DatabaseManager('sqlite:///../university-cost-mcp/universities.db')
all_unis = db.search_universities('', limit=50)

print(f'Total universities in database: {len(all_unis)}')
print('\nAll universities:')
for uni in all_unis:
    print(f"  - {uni.get('university_name')} ({uni.get('degree_level')})")

print('\n\nSearching for Rutgers:')
rutgers_results = db.search_universities('Rutgers', limit=10)
print(f'Found {len(rutgers_results)} Rutgers entries:')
for uni in rutgers_results:
    print(f"  - {uni.get('university_name')} - {uni.get('degree_level')} - Tuition: {uni.get('international_tuition')}")

print('\n\nSearching for "Rutgers New Brunswick":')
rutgers_nb = db.get_university_by_name('Rutgers New Brunswick', 'master')
print(f'Direct search result: {len(rutgers_nb)} entries')
for uni in rutgers_nb:
    print(f"  - {uni.get('university_name')} - {uni.get('degree_level')}")

print('\n\nSearching for "Rutgers University-New Brunswick":')
rutgers_exact = db.get_university_by_name('Rutgers University-New Brunswick', 'master')
print(f'Exact name search result: {len(rutgers_exact)} entries')
for uni in rutgers_exact:
    print(f"  - {uni.get('university_name')} - {uni.get('degree_level')} - Tuition: {uni.get('international_tuition')}")
