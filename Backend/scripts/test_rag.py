#!/usr/bin/env python3
"""
Test script for RAG system
"""

import json
from pathlib import Path

def test_setup():
    print("="*60)
    print("🧪 TESTING RAG SYSTEM SETUP")
    print("="*60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Check folder structure
    print("\n[Test 1] Checking folder structure...")
    tests_total += 1
    required_dirs = [
        "cooking_assistant/rag/data/recipes",
        "cooking_assistant/rag/data/processed",
        "cooking_assistant/rag/pdfs",
        "scripts"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        exists = Path(dir_path).exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {dir_path}")
        if not exists:
            all_exist = False
    
    if all_exist:
        tests_passed += 1
        print("  ✅ Folder structure OK")
    else:
        print("  ❌ Some folders missing")
    
    # Test 2: Check recipe database
    print("\n[Test 2] Checking recipe database...")
    tests_total += 1
    db_path = Path("cooking_assistant/rag/data/recipe_database.json")
    
    if db_path.exists():
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                recipe_count = len(data.get('recipes', []))
                print(f"  ✅ Recipe database exists with {recipe_count} recipes")
                tests_passed += 1
        except Exception as e:
            print(f"  ❌ Error reading database: {e}")
    else:
        print("  ⚠️  Recipe database not created yet")
    
    # Test 3: Check for recipe files
    print("\n[Test 3] Checking recipe files...")
    tests_total += 1
    recipe_dir = Path("cooking_assistant/rag/data/recipes")
    recipe_files = list(recipe_dir.glob("recipe_*.json"))
    
    if recipe_files:
        valid_recipes = 0
        for recipe_file in recipe_files:
            try:
                with open(recipe_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        json.loads(content)
                        valid_recipes += 1
            except:
                pass
        
        print(f"  ✅ Found {len(recipe_files)} recipe files ({valid_recipes} valid)")
        if valid_recipes > 0:
            tests_passed += 1
    else:
        print("  ⚠️  No recipe files found")
    
    # Test 4: Check Python modules
    print("\n[Test 4] Checking Python dependencies...")
    tests_total += 1
    
    try:
        import flask
        import pymongo
        import pandas
        import numpy
        import torch
        import transformers
        print("  ✅ All required packages installed")
        tests_passed += 1
    except ImportError as e:
        print(f"  ❌ Missing package: {e}")
    
    # Summary
    print("\n" + "="*60)
    print(f"📊 TEST RESULTS: {tests_passed}/{tests_total} tests passed")
    print("="*60)
    
    if tests_passed == tests_total:
        print("✅ All tests passed! System is ready.")
    elif tests_passed > 0:
        print("⚠️  Some tests passed. Review the issues above.")
    else:
        print("❌ Setup incomplete. Please run setup_rag.py first.")

if __name__ == "__main__":
    test_setup()