"""
Comparison of Dictionary Sorting Implementations
Demonstrates different approaches to sorting lists of dictionaries by a specific key
"""

import time
from typing import List, Dict, Any

# Sample data for testing
sample_data = [
    {'name': 'Alice', 'age': 30, 'score': 85},
    {'name': 'Bob', 'age': 25, 'score': 92},
    {'name': 'Charlie', 'age': 35, 'score': 78},
    {'name': 'Diana', 'age': 28, 'score': 95},
    {'name': 'Eve', 'age': 32, 'score': 88}
]

# ============= IMPLEMENTATION 1: AI-Optimized (sorted with lambda) =============
def sort_by_key_optimized(data: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    """
    Most Pythonic and efficient approach using built-in sorted() with lambda.
    Time Complexity: O(n log n) - Timsort algorithm
    Space Complexity: O(n) - creates new sorted list
    """
    return sorted(data, key=lambda x: x[key], reverse=reverse)


# ============= IMPLEMENTATION 2: Manual with operator.itemgetter =============
def sort_by_key_itemgetter(data: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    """
    Using operator.itemgetter - slightly faster than lambda for simple key access.
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    from operator import itemgetter
    return sorted(data, key=itemgetter(key), reverse=reverse)


# ============= IMPLEMENTATION 3: Manual Bubble Sort =============
def sort_by_key_manual_bubble(data: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    """
    Manual implementation using bubble sort algorithm.
    Time Complexity: O(n²) - Very inefficient for large datasets
    Space Complexity: O(n) - creates copy of list
    """
    result = data.copy()
    n = len(result)
    
    for i in range(n):
        for j in range(0, n - i - 1):
            condition = result[j][key] > result[j + 1][key]
            if reverse:
                condition = not condition
            if condition:
                result[j], result[j + 1] = result[j + 1], result[j]
    
    return result


# ============= IMPLEMENTATION 4: In-place sort =============
def sort_by_key_inplace(data: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    """
    In-place sorting using list.sort() method.
    Time Complexity: O(n log n)
    Space Complexity: O(1) - sorts in place (more memory efficient)
    """
    data.sort(key=lambda x: x[key], reverse=reverse)
    return data


# ============= PERFORMANCE TESTING =============
def benchmark_sorting_methods(data: List[Dict[str, Any]], key: str, iterations: int = 1000):
    """Benchmark different sorting implementations"""
    
    print("=" * 70)
    print(f"PERFORMANCE COMPARISON (sorting by '{key}', {iterations} iterations)")
    print("=" * 70)
    
    methods = [
        ("AI-Optimized (sorted + lambda)", sort_by_key_optimized),
        ("operator.itemgetter", sort_by_key_itemgetter),
        ("Manual Bubble Sort", sort_by_key_manual_bubble),
        ("In-place sort()", lambda d, k, r=False: sort_by_key_inplace(d.copy(), k, r))
    ]
    
    for name, func in methods:
        start = time.perf_counter()
        for _ in range(iterations):
            result = func(data.copy(), key)
        elapsed = time.perf_counter() - start
        
        print(f"\n{name}:")
        print(f"  Total time: {elapsed:.4f}s")
        print(f"  Avg per iteration: {(elapsed/iterations)*1000:.4f}ms")


# ============= DEMONSTRATION =============
if __name__ == "__main__":
    print("Original data:")
    for item in sample_data:
        print(f"  {item}")
    
    print("\n" + "=" * 70)
    print("SORTING BY 'score' (descending)")
    print("=" * 70)
    
    # Test each implementation
    implementations = [
        ("AI-Optimized", sort_by_key_optimized),
        ("itemgetter", sort_by_key_itemgetter),
        ("Bubble Sort", sort_by_key_manual_bubble),
        ("In-place", lambda d, k, r: sort_by_key_inplace(d.copy(), k, r))
    ]
    
    for name, func in implementations:
        result = func(sample_data.copy(), 'score', reverse=True)
        print(f"\n{name} result:")
        for item in result:
            print(f"  {item}")
    
    # Run performance benchmark
    print("\n")
    benchmark_sorting_methods(sample_data, 'score', iterations=10000)
    
    print("\n" + "=" * 70)
    print("HANDLING MISSING KEYS")
    print("=" * 70)
    
    # Safe version with default value
    def sort_by_key_safe(data: List[Dict[str, Any]], key: str, 
                         default=0, reverse: bool = False) -> List[Dict[str, Any]]:
        """Safe sorting with default value for missing keys"""
        return sorted(data, key=lambda x: x.get(key, default), reverse=reverse)
    
    incomplete_data = sample_data + [{'name': 'Frank', 'age': 40}]  # Missing 'score'
    result = sort_by_key_safe(incomplete_data, 'score', default=0, reverse=True)
    print("\nSafe sorting with missing keys:")
    for item in result:
        print(f"  {item}")
