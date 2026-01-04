#!/usr/bin/env python3
"""
Main setup script for RAG system
Run this FIRST to set up everything!
"""

import os
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def main():
    print("="*60)
    print("🚀 SETTING UP RAG SYSTEM")
    print("="*60)
    
    # Step 1: Combine individual recipes
    print("\n[1/4] Combining recipe files...")
    combine_recipes()
    
    # Step 2: Create basic structure (skip PDF extraction for now)
    print("\n[2/4] Creating data structure...")
    create_data_structure()
    
    # Step 3: Create basic embeddings preparation
    print("\n[3/4] Preparing recipe data...")
    prepare_recipe_data()
    
    # Step 4: Summary
    print("\n[4/4] Setup summary...")
    show_summary()
    
    print("\n" + "="*60)
    print("✅ BASIC SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Add your recipe data to the JSON files in cooking_assistant/rag/data/recipes/")
    print("2. Optionally add PDF cookbooks to cooking_assistant/rag/pdfs/")
    print("3. Run this script again to process everything")

def combine_recipes():
    """Combine all individual recipe JSON files"""
    recipe_dir = Path("cooking_assistant/rag/data/recipes")
    recipes = []
    
    # Check if recipe files exist
    recipe_files = list(recipe_dir.glob("recipe_*.json"))
    
    if not recipe_files:
        print("  ⚠️  No recipe files found yet")
        return
    
    for recipe_file in sorted(recipe_files):
        try:
            with open(recipe_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:  # Only process non-empty files
                    recipe = json.loads(content)
                    recipes.append(recipe)
        except json.JSONDecodeError:
            print(f"  ⚠️  Skipping {recipe_file.name} (empty or invalid JSON)")
        except Exception as e:
            print(f"  ⚠️  Error reading {recipe_file.name}: {e}")
    
    if not recipes:
        print("  ⚠️  No valid recipes found to combine")
        return
    
    # Save combined
    output = {
        "metadata": {
            "total_recipes": len(recipes),
            "languages": ["english"],
            "source": "Manual entry"
        },
        "recipes": recipes
    }
    
    output_path = Path("cooking_assistant/rag/data/recipe_database.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ Combined {len(recipes)} recipes")

def create_data_structure():
    """Create necessary data directories"""
    dirs = [
        "cooking_assistant/rag/data/processed",
        "cooking_assistant/rag/data/embeddings",
        "models",
        "cooking_assistant/rag/pdfs"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("  ✅ Created data directories")

def prepare_recipe_data():
    """Prepare recipe data for processing"""
    recipe_db_path = Path("cooking_assistant/rag/data/recipe_database.json")
    
    if not recipe_db_path.exists():
        print("  ⚠️  No recipe database found - create some recipes first!")
        return
    
    with open(recipe_db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Save to processed directory
    processed_path = Path("cooking_assistant/rag/data/processed/recipes_processed.json")
    with open(processed_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ Prepared {len(data.get('recipes', []))} recipes for processing")

def show_summary():
    """Show setup summary"""
    recipe_db = Path("cooking_assistant/rag/data/recipe_database.json")
    
    if recipe_db.exists():
        with open(recipe_db, 'r', encoding='utf-8') as f:
            data = json.load(f)
            recipe_count = len(data.get('recipes', []))
            print(f"  📊 Total recipes in database: {recipe_count}")
    else:
        print("  📊 No recipes in database yet")
    
    # Check for PDFs
    pdf_dir = Path("cooking_assistant/rag/pdfs")
    pdf_count = len(list(pdf_dir.glob("*.pdf"))) if pdf_dir.exists() else 0
    print(f"  📄 PDF cookbooks found: {pdf_count}")

if __name__ == "__main__":
    main()