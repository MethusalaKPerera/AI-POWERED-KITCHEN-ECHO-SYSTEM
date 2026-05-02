#!/usr/bin/env python3
"""
Web Recipe Scraper for Sri Lankan Recipe Sites
Alternative to PDF extraction - scrapes from working websites
Requires: pip install beautifulsoup4 requests --break-system-packages
"""

import json
import re
from pathlib import Path
import time

try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False
    print("⚠️ Web scraping libraries not installed!")
    print("Install with: pip install beautifulsoup4 requests --break-system-packages")

def scrape_islandsmile_recipe(url):
    """Scrape a single recipe from islandsmile.org"""
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract recipe details (adjust selectors based on site structure)
        recipe = {
            'name': '',
            'ingredients': [],
            'instructions': [],
            'description': ''
        }
        
        # Title
        title_elem = soup.find('h1', class_='entry-title') or soup.find('h1')
        if title_elem:
            recipe['name'] = title_elem.get_text().strip()
        
        # Ingredients (common patterns)
        ing_section = soup.find('div', class_='ingredients') or soup.find('ul', class_='ingredients')
        if ing_section:
            for li in ing_section.find_all('li'):
                text = li.get_text().strip()
                if text:
                    recipe['ingredients'].append(text)
        
        # Instructions
        inst_section = soup.find('div', class_='instructions') or soup.find('ol', class_='instructions')
        if inst_section:
            for li in inst_section.find_all('li'):
                text = li.get_text().strip()
                if text:
                    recipe['instructions'].append(text)
        
        # Description
        desc_elem = soup.find('div', class_='entry-content')
        if desc_elem:
            paragraphs = desc_elem.find_all('p', limit=2)
            if paragraphs:
                recipe['description'] = paragraphs[0].get_text().strip()[:200]
        
        return recipe if recipe['name'] and recipe['ingredients'] else None
        
    except Exception as e:
        print(f"  ❌ Error scraping {url}: {e}")
        return None

def get_recipe_urls_from_sitemap(base_url):
    """Get list of recipe URLs from website"""
    
    # Common patterns for Sri Lankan recipe sites
    recipe_urls = []
    
    try:
        # Try sitemap
        sitemap_url = f"{base_url}/sitemap.xml"
        response = requests.get(sitemap_url, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'xml')
            for loc in soup.find_all('loc'):
                url = loc.get_text()
                if 'recipe' in url.lower() or 'food' in url.lower():
                    recipe_urls.append(url)
        
    except:
        pass
    
    return recipe_urls[:50]  # Limit to 50 recipes

def manual_recipe_list():
    """Manually curated list of working recipe URLs"""
    
    return [
        # Working URLs from islandsmile.org
        "https://www.islandsmile.org/sri-lankan-fish-cutlets/",
        "https://www.islandsmile.org/coconut-rice/",
        "https://www.islandsmile.org/roast-paan/",
        "https://www.islandsmile.org/kibula-banis/",
        "https://www.islandsmile.org/sri-lankan-yellow-rice/",
        "https://www.islandsmile.org/ambulthiyal/",
        "https://www.islandsmile.org/jackfruit-curry/",
        "https://www.islandsmile.org/spicy-cabbage-stir-fry/",
        "https://www.islandsmile.org/fried-fish-steaks/",
        "https://www.islandsmile.org/karawala-thel-dala/",
    ]

def scrape_and_convert_recipes(urls, start_id=153):
    """Scrape recipes from URLs and convert to our JSON format"""
    
    print("\n" + "="*70)
    print("WEB RECIPE SCRAPER")
    print("="*70 + "\n")
    
    if not SCRAPER_AVAILABLE:
        return []
    
    recipes = []
    recipe_id = start_id
    
    print(f"Scraping {len(urls)} recipe URLs...\n")
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Scraping: {url}")
        
        scraped = scrape_islandsmile_recipe(url)
        
        if scraped and scraped['ingredients']:
            # Convert to our format
            recipe = {
                "id": f"recipe_{recipe_id:03d}",
                "name": scraped['name'],
                "name_sinhala": "",  # To be translated
                "name_tamil": "",    # To be translated
                "category": "Curry",  # Default, can be improved
                "region": "General",
                "description": scraped['description'],
                "ingredients": scraped['ingredients'],
                "instructions": scraped['instructions'],
                "prep_time_minutes": 30,
                "cook_time_minutes": 30,
                "servings": 4,
                "difficulty": "Medium",
                "tags": ["web-scraped", "islandsmile"],
                "cultural_notes": f"Recipe from {url}",
                "authenticity_score": 0.90
            }
            
            recipes.append(recipe)
            recipe_id += 1
            print(f"  ✅ Extracted: {recipe['name']} ({len(recipe['ingredients'])} ingredients)")
        else:
            print(f"  ⚠️ Could not extract recipe")
        
        time.sleep(1)  # Be polite to server
    
    print(f"\n✅ Successfully scraped {len(recipes)} recipes")
    return recipes

def save_scraped_recipes(recipes, output_dir='rag/data/recipes'):
    """Save scraped recipes to database"""
    
    if not recipes:
        print("\n⚠️ No recipes to save")
        return
    
    print(f"\n💾 Saving {len(recipes)} recipes...")
    
    db_path = Path(output_dir) / 'recipe_database.json'
    
    # Load existing
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            existing_recipes = data.get('recipes', [])
    except FileNotFoundError:
        existing_recipes = []
    
    # Merge
    all_recipes = existing_recipes + recipes
    
    # Save combined
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total_recipes': len(all_recipes),
            'created_date': '2026-01-02',
            'recipes': all_recipes
        }, f, indent=2, ensure_ascii=False)
    
    # Save individual files
    for recipe in recipes:
        recipe_file = Path(output_dir) / f"{recipe['id']}.json"
        with open(recipe_file, 'w', encoding='utf-8') as f:
            json.dump(recipe, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Saved to: {output_dir}")
    print(f"   ✅ Total recipes: {len(all_recipes)}")

def main():
    """Main scraper workflow"""
    
    print("\n" + "="*70)
    print("SRI LANKAN RECIPE WEB SCRAPER")
    print("="*70)
    
    if not SCRAPER_AVAILABLE:
        print("\n❌ Required libraries not installed!")
        print("\nInstall with:")
        print("  pip install beautifulsoup4 requests --break-system-packages")
        return
    
    print("\nThis scraper extracts recipes from Sri Lankan recipe websites")
    print("\nRecommended sites:")
    print("  • https://islandsmile.org")
    print("  • https://www.malaikitchen.com")
    print("  • https://www.thalinomnom.com")
    
    print("\nOptions:")
    print("  1. Scrape manually added URLs (quick - 3 recipes)")
    print("  2. Add your own URLs (custom)")
    print("  3. Skip web scraping for now")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        urls = manual_recipe_list()
        recipes = scrape_and_convert_recipes(urls)
        save_scraped_recipes(recipes)
    
    elif choice == "2":
        print("\nEnter recipe URLs (one per line, empty line to finish):")
        urls = []
        while True:
            url = input("URL: ").strip()
            if not url:
                break
            urls.append(url)
        
        if urls:
            recipes = scrape_and_convert_recipes(urls)
            save_scraped_recipes(recipes)
    
    else:
        print("\nSkipping web scraping")
    
    print("\n" + "="*70)
    print("Next steps:")
    print("  1. Translate recipes: python auto_translate_all.py")
    print("  2. Rebuild RAG: python recipe_rag_system.py")
    print("="*70)

if __name__ == "__main__":
    main()