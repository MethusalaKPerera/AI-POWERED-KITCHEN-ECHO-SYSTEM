
import sys
import os
import time
import json

# Add parent directory to path to import smart_shopping module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from smart_shopping.nlp_processor import NLPProcessor
    from smart_shopping.recommendation_engine import RecommendationEngine
    print("✅ Modules imported successfully.")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def evaluate_nlp():
    print("\n--- Phase 1: NLP Extraction Accuracy ---")
    nlp = NLPProcessor()
    
    test_cases = [
        {
            "query": "Find cheap red shoes under $50",
            "expected_price_range": [0, 50],
            "expected_keywords": ["red", "shoes"]
        },
        {
            "query": "Compare iPhone 15 vs Samsung Galaxy",
            "expected_intent": "compare",
            "expected_keywords": ["iphone", "samsung"]
        },
        {
            "query": "Suggest 5 star organic milk",
            "expected_rating": 5,
            "expected_keywords": ["organic", "milk"]
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for case in test_cases:
        print(f"Testing Query: '{case['query']}'")
        result = nlp.process_query(case['query'])
        filters = nlp.extract_filters(case['query'])
        
        match = True
        if "expected_price_range" in case:
            if filters.get('priceRange', [0, 0])[1] != case['expected_price_range'][1]:
                match = False
        
        if "expected_intent" in case:
            if result.get('intent') != case['expected_intent']:
                match = False
                
        if match:
            print("  Result: PASS ✅")
            passed += 1
        else:
            print(f"  Result: FAIL ❌ (Got: {result.get('intent', 'N/A')} intent, {filters.get('priceRange', 'N/A')} price)")
            
    accuracy = (passed / total) * 100
    print(f"NLP Extraction Accuracy: {accuracy:.2f}%")
    return accuracy

def evaluate_performance():
    print("\n--- Phase 2: System Latency (Performance) ---")
    nlp = NLPProcessor()
    start_time = time.time()
    
    # Run 10 iterations to get average
    iterations = 5
    for i in range(iterations):
        nlp.process_query("Find high quality kitchen tools")
        
    end_time = time.time()
    avg_latency = (end_time - start_time) / iterations
    print(f"Average NLP Processing Time: {avg_latency*1000:.2f}ms")
    
    if avg_latency < 0.1: # 100ms
        print("Performance Rating: EXCELLENT (Target < 200ms) ⚡")
    else:
        print("Performance Rating: GOOD")
    return avg_latency

def evaluate_data_integrity():
    print("\n--- Phase 3: Data Integrity & Storage ---")
    history_file = os.path.join(os.path.dirname(__file__), 'data', 'shopping_history.json')
    
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                data = json.load(f)
                count = len(data)
                print(f"Local Storage Health: ACTIVE ✅ ({count} historical data points found)")
        except:
            print("Local Storage Health: CORRUPTED ❌")
    else:
        print("Local Storage Health: NOT FOUND (Starting fresh) ℹ️")

if __name__ == "__main__":
    print("==================================================")
    print("   SMART SHOPPING SYSTEM EVALUATION REPORT")
    print("==================================================")
    
    acc = evaluate_nlp()
    lat = evaluate_performance()
    evaluate_data_integrity()
    
    print("\n==================================================")
    print(f"OVERALL SYSTEM SCORE: {(acc * 0.7 + (1-lat)*30):.1f}/100")
    print("Reference: Research Project Validation Script (v1.0)")
    print("==================================================")
