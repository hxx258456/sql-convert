#!/usr/bin/env python3
"""
Test script for SQL Converter API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:", response.json())
    return response.status_code == 200

def test_convert_simple():
    """Test simple SQL conversion"""
    mysql_sql = "SELECT * FROM users WHERE age > 18"
    
    data = {
        "mysql_sql": mysql_sql,
        "pretty": True
    }
    
    response = requests.post(f"{BASE_URL}/convert", json=data)
    result = response.json()
    
    print("\nSimple Conversion Test:")
    print(f"MySQL SQL: {result['mysql_sql']}")
    print(f"Oracle SQL: {result['oracle_sql']}")
    print(f"Success: {result['success']}")
    
    return result['success']

def test_convert_complex():
    """Test complex SQL conversion"""
    mysql_sql = """
    SELECT 
        u.id,
        u.name,
        u.email,
        COUNT(o.id) as order_count
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.created_at >= '2023-01-01'
    GROUP BY u.id, u.name, u.email
    HAVING order_count > 0
    ORDER BY order_count DESC
    LIMIT 10
    """
    
    data = {
        "mysql_sql": mysql_sql,
        "pretty": True
    }
    
    response = requests.post(f"{BASE_URL}/convert", json=data)
    result = response.json()
    
    print("\nComplex Conversion Test:")
    print(f"MySQL SQL: {result['mysql_sql']}")
    print(f"Oracle SQL: {result['oracle_sql']}")
    print(f"Success: {result['success']}")
    
    return result['success']

def test_convert_batch():
    """Test batch SQL conversion"""
    mysql_queries = [
        "SELECT * FROM products WHERE price > 100",
        "INSERT INTO users (name, email) VALUES ('John', 'john@example.com')",
        "UPDATE users SET status = 'active' WHERE id = 1"
    ]
    
    requests_data = [
        {"mysql_sql": sql, "pretty": True} for sql in mysql_queries
    ]
    
    response = requests.post(f"{BASE_URL}/convert/batch", json=requests_data)
    results = response.json()
    
    print("\nBatch Conversion Test:")
    for i, result in enumerate(results):
        print(f"\nQuery {i+1}:")
        print(f"MySQL: {result['mysql_sql']}")
        print(f"Oracle: {result['oracle_sql']}")
        print(f"Success: {result['success']}")
    
    return all(result['success'] for result in results)

def main():
    """Run all tests"""
    print("Testing SQL Converter API...")
    
    # Test health endpoint
    if not test_health():
        print("❌ Health check failed")
        return
    
    print("✅ Health check passed")
    
    # Test simple conversion
    if test_convert_simple():
        print("✅ Simple conversion passed")
    else:
        print("❌ Simple conversion failed")
    
    # Test complex conversion
    if test_convert_complex():
        print("✅ Complex conversion passed")
    else:
        print("❌ Complex conversion failed")
    
    # Test batch conversion
    if test_convert_batch():
        print("✅ Batch conversion passed")
    else:
        print("❌ Batch conversion failed")

if __name__ == "__main__":
    main() 