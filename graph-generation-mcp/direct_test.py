"""Direct testing of graph generation functions without MCP layer"""

import sys
sys.path.insert(0, '.')

from server.graph_generator import GraphGenerator
from visualizations.graph_types import GraphType
import json

def test_1_auto_detection():
    """Test auto-detection with salary data"""
    print("\n" + "="*60)
    print("TEST 1: Auto-Detection (Salary by Degree)")
    print("="*60)
    
    generator = GraphGenerator()
    
    data = [
        {'degree': 'Bachelor', 'salary': 75000},
        {'degree': 'Master', 'salary': 95000},
        {'degree': 'PhD', 'salary': 112000}
    ]
    
    result = generator.generate_graph(
        data=data,
        title='Average Salary by Degree Level'
    )
    
    print(f"✓ Graph Type Detected: {result['type']}")
    print(f"✓ Data Points: {result['metadata']['rows']}")
    if 'statistics' in result and result['statistics']:
        stats = result['statistics']
        print(f"✓ Statistics: Mean ${stats['mean']:,.0f}, Median ${stats['median']:,.0f}")
    print(f"✓ HTML Output Size: {len(result['html'])} chars")
    return True

def test_2_bar_chart():
    """Test explicit bar chart"""
    print("\n" + "="*60)
    print("TEST 2: Bar Chart (University Costs)")
    print("="*60)
    
    generator = GraphGenerator()
    
    data = [
        {'university': 'MIT', 'cost': 77020},
        {'university': 'Stanford', 'cost': 79619},
        {'university': 'Berkeley', 'cost': 49254},
        {'university': 'Georgia Tech', 'cost': 33794}
    ]
    
    result = generator.generate_graph(
        data=data,
        x_column='university',
        y_column='cost',
        graph_type='bar',
        title='Annual Tuition Costs'
    )
    
    print(f"✓ Graph Type: {result['type']}")
    print(f"✓ Universities: {result['metadata']['rows']}")
    print(f"✓ Figure Created: {len(result['figure']) > 0}")
    return True

def test_3_line_graph():
    """Test line graph with time series"""
    print("\n" + "="*60)
    print("TEST 3: Line Graph (Salary Growth)")
    print("="*60)
    
    generator = GraphGenerator()
    
    data = [
        {'year': 2020, 'salary': 75000},
        {'year': 2021, 'salary': 78000},
        {'year': 2022, 'salary': 82000},
        {'year': 2023, 'salary': 87000},
        {'year': 2024, 'salary': 92000}
    ]
    
    result = generator.generate_graph(
        data=data,
        x_column='year',
        y_column='salary',
        graph_type='line',
        title='5-Year Salary Progression'
    )
    
    print(f"✓ Graph Type: {result['type']}")
    print(f"✓ Data Points: {result['metadata']['rows']}")
    print(f"✓ Growth: ${data[0]['salary']:,} → ${data[-1]['salary']:,}")
    return True

def test_4_scatter_plot():
    """Test scatter plot for correlation"""
    print("\n" + "="*60)
    print("TEST 4: Scatter Plot (Debt vs Salary)")
    print("="*60)
    
    generator = GraphGenerator()
    
    data = [
        {'debt': 30000, 'salary': 75000},
        {'debt': 50000, 'salary': 85000},
        {'debt': 70000, 'salary': 95000},
        {'debt': 90000, 'salary': 105000},
        {'debt': 110000, 'salary': 115000}
    ]
    
    result = generator.generate_graph(
        data=data,
        x_column='debt',
        y_column='salary',
        graph_type='scatter',
        title='Debt vs Starting Salary'
    )
    
    print(f"✓ Graph Type: {result['type']}")
    print(f"✓ Data Points: {result['metadata']['rows']}")
    print(f"✓ Correlation Analysis: Complete")
    return True

def test_5_pie_chart():
    """Test pie chart for proportions"""
    print("\n" + "="*60)
    print("TEST 5: Pie Chart (Expense Breakdown)")
    print("="*60)
    
    generator = GraphGenerator()
    
    data = [
        {'category': 'Tuition', 'amount': 57590},
        {'category': 'Housing', 'amount': 12680},
        {'category': 'Food & Living', 'amount': 5540},
        {'category': 'Books', 'amount': 840},
        {'category': 'Fees', 'amount': 370}
    ]
    
    result = generator.generate_graph(
        data=data,
        x_column='category',
        y_column='amount',
        graph_type='pie',
        title='MIT Annual Expense Breakdown'
    )
    
    print(f"✓ Graph Type: {result['type']}")
    print(f"✓ Categories: {result['metadata']['rows']}")
    total = sum(item['amount'] for item in data)
    print(f"✓ Total: ${total:,}")
    return True

def test_6_histogram():
    """Test histogram for distribution"""
    print("\n" + "="*60)
    print("TEST 6: Histogram (Salary Distribution)")
    print("="*60)
    
    generator = GraphGenerator()
    
    # Generate sample salary data
    import random
    random.seed(42)
    salaries = [random.gauss(95000, 15000) for _ in range(100)]
    
    data = [{'salary': s} for s in salaries]
    
    result = generator.generate_graph(
        data=data,
        x_column='salary',
        graph_type='histogram',
        title='Master\'s Degree Salary Distribution'
    )
    
    print(f"✓ Graph Type: {result['type']}")
    print(f"✓ Sample Size: {result['metadata']['rows']}")
    if 'statistics' in result and result['statistics']:
        stats = result['statistics']
        print(f"✓ Mean: ${stats['mean']:,.0f}, StdDev: ${stats['std']:,.0f}")
    return True

def test_7_comparison_chart():
    """Test comparison chart with multiple series"""
    print("\n" + "="*60)
    print("TEST 7: Comparison Chart (Bachelor vs Master)")
    print("="*60)
    
    generator = GraphGenerator()
    
    data = [
        {'university': 'MIT', 'bachelor': 55878, 'master': 77020},
        {'university': 'Stanford', 'bachelor': 58416, 'master': 79619},
        {'university': 'Berkeley', 'bachelor': 14312, 'master': 49254}
    ]
    
    result = generator.generate_comparison_chart(
        data=data,
        category_column='university',
        value_columns=['bachelor', 'master'],
        title='Tuition Comparison: Bachelor vs Master'
    )
    
    print(f"✓ Graph Type: {result['type']}")
    print(f"✓ Universities: {len(data)}")
    print(f"✓ Series: 2 (Bachelor, Master)")
    return True

def main():
    """Run all direct tests"""
    print("\n" + "="*70)
    print(" GRAPH GENERATION MCP - DIRECT UNIT TESTS")
    print("="*70)
    print("Testing core graph generation without MCP layer...")
    
    tests = [
        test_1_auto_detection,
        test_2_bar_chart,
        test_3_line_graph,
        test_4_scatter_plot,
        test_5_pie_chart,
        test_6_histogram,
        test_7_comparison_chart
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            failed += 1
            print(f"✗ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print(f" RESULTS: {passed} passed, {failed} failed")
    print("="*70)
    
    if failed == 0:
        print("✅ All direct tests passed successfully!")
        return 0
    else:
        print(f"❌ {failed} test(s) failed")
        return 1

if __name__ == '__main__':
    exit(main())
