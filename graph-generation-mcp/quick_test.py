"""Quick import and basic functionality test"""

print("Testing imports...")

try:
    from server.graph_generator import GraphGenerator
    print("✓ GraphGenerator imported")
except Exception as e:
    print(f"✗ GraphGenerator import failed: {e}")
    exit(1)

try:
    from visualizations.data_processor import DataProcessor
    print("✓ DataProcessor imported")
except Exception as e:
    print(f"✗ DataProcessor import failed: {e}")
    exit(1)

try:
    from visualizations.plotly_engine import PlotlyEngine
    print("✓ PlotlyEngine imported")
except Exception as e:
    print(f"✗ PlotlyEngine import failed: {e}")
    exit(1)

# Quick functional test
print("\nTesting basic functionality...")
generator = GraphGenerator()
result = generator.generate_graph(
    data=[
        {'degree': 'Bachelor', 'salary': 75000},
        {'degree': 'Master', 'salary': 95000}
    ],
    title='Test Graph'
)

print(f"✓ Graph generated: {result['type']}")
print(f"✓ HTML size: {len(result['html'])} chars")
print(f"✓ Figure exists: {len(result['figure']) > 0}")

print("\n✅ All basic tests passed!")
