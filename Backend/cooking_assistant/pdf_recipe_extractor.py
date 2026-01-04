#!/usr/bin/env python3
"""
PDF Recipe Extractor
Extracts recipes from PDF cookbooks and converts to JSON format
Requires: pip install PyPDF2 pdfplumber --break-system-packages
"""

import json
import re
from pathlib import Path

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ PDF libraries not installed!")
    print("Install with: pip install pdfplumber PyPDF2 --break-system-packages")

def extract_text_from_pdf(pdf_path):
    """Extract all text from PDF file"""
    
    if not PDF_AVAILABLE:
        return None
    
    print(f"\n📄 Reading PDF: {pdf_path}")
    
    full_text = ""
    page_count = 0
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)
            print(f"   Pages: {page_count}")
            
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    full_text += f"\n--- PAGE {i} ---\n{text}"
                
                if i % 10 == 0:
                    print(f"   Processed {i}/{page_count} pages...")
        
        print(f"   ✅ Extracted {len(full_text)} characters")
        return full_text
    
    except Exception as e:
        print(f"   ❌ Error reading PDF: {e}")
        return None

def parse_recipes_from_text(text, start_id=153):
    """
    Parse recipes from extracted text
    This is a basic parser - you may need to customize based on PDF format
    """
    
    print("\n🔍 Parsing recipes from text...")
    
    recipes = []
    recipe_id = start_id
    
    # Split by common recipe delimiters
    # Adjust these patterns based on your PDF cookbook format
    potential_recipes = re.split(r'\n(?=[A-Z][A-Z\s]+\n)', text)
    
    print(f"   Found {len(potential_recipes)} potential recipe sections")
    
    for section in potential_recipes:
        lines = section.strip().split('\n')
        
        if len(lines) < 5:  # Too short to be a recipe
            continue
        
        # Try to extract recipe name (usually first line in CAPS or Title Case)
        name = lines[0].strip()
        
        if len(name) < 5 or len(name) > 100:  # Invalid name length
            continue
        
        # Basic recipe structure
        recipe = {
            "id": f"recipe_{recipe_id:03d}",
            "name": name.title(),
            "name_sinhala": "",  # To be translated
            "name_tamil": "",    # To be translated
            "category": "Curry",  # Default, can be improved
            "region": "General",
            "description": "",
            "ingredients": [],
            "instructions": [],
            "prep_time_minutes": 30,
            "cook_time_minutes": 30,
            "servings": 4,
            "difficulty": "Medium",
            "tags": ["pdf-extracted"],
            "cultural_notes": f"Extracted from cookbook",
            "authenticity_score": 0.85
        }
        
        # Try to extract ingredients and instructions
        in_ingredients = False
        in_instructions = False
        
        for line in lines[1:]:
            line = line.strip()
            
            if not line:
                continue
            
            # Detect ingredients section
            if re.match(r'ingredients?:?', line, re.IGNORECASE):
                in_ingredients = True
                in_instructions = False
                continue
            
            # Detect instructions section
            if re.match(r'(method|instructions?|directions?|preparation):?', line, re.IGNORECASE):
                in_instructions = True
                in_ingredients = False
                continue
            
            # Add to appropriate section
            if in_ingredients:
                if line and len(line) < 200:  # Reasonable ingredient length
                    recipe['ingredients'].append(line)
            elif in_instructions:
                if line and len(line) < 500:  # Reasonable instruction length
                    recipe['instructions'].append(line)
            elif not recipe['description'] and len(line) > 20:
                recipe['description'] = line[:200]  # First meaningful line as description
        
        # Only add if we found ingredients
        if len(recipe['ingredients']) >= 3:
            recipes.append(recipe)
            recipe_id += 1
            print(f"   ✅ Extracted: {recipe['name']} ({len(recipe['ingredients'])} ingredients)")
    
    print(f"\n   Total recipes extracted: {len(recipes)}")
    return recipes

def save_extracted_recipes(recipes, output_dir='rag/data/recipes'):
    """Save extracted recipes to database"""
    
    print(f"\n💾 Saving {len(recipes)} recipes...")
    
    db_path = Path(output_dir) / 'recipe_database.json'
    
    # Load existing recipes
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            existing_recipes = data.get('recipes', [])
    except FileNotFoundError:
        existing_recipes = []
    
    # Merge
    all_recipes = existing_recipes + recipes
    
    # Save combined database
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total_recipes': len(all_recipes),
            'created_date': '2026-01-02',
            'recipes': all_recipes
        }, f, indent=2, ensure_ascii=False)
    
    # Save individual recipe files
    for recipe in recipes:
        recipe_file = Path(output_dir) / f"{recipe['id']}.json"
        with open(recipe_file, 'w', encoding='utf-8') as f:
            json.dump(recipe, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Saved to: {output_dir}")
    print(f"   ✅ Total recipes in database: {len(all_recipes)}")

def process_pdf_cookbook(pdf_path):
    """Main function to process a PDF cookbook"""
    
    print("\n" + "="*70)
    print("PDF RECIPE EXTRACTOR")
    print("="*70)
    
    if not PDF_AVAILABLE:
        print("\n❌ PDF libraries not installed!")
        print("\nInstall with:")
        print("  pip install pdfplumber PyPDF2 --break-system-packages")
        return
    
    # Check if PDF exists
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"\n❌ PDF file not found: {pdf_path}")
        print("\nPlace your PDF file in the project folder and try again.")
        return
    
    # Extract text
    text = extract_text_from_pdf(pdf_path)
    
    if not text:
        print("\n❌ Could not extract text from PDF")
        return
    
    # Parse recipes
    recipes = parse_recipes_from_text(text)
    
    if not recipes:
        print("\n⚠️ No recipes found!")
        print("   The PDF format may require custom parsing.")
        print("   You can manually adjust the parse_recipes_from_text() function.")
        return
    
    # Save recipes
    save_extracted_recipes(recipes)
    
    print("\n" + "="*70)
    print("✅ PDF EXTRACTION COMPLETE!")
    print("="*70)
    print(f"\nNext steps:")
    print("  1. Review extracted recipes in rag/data/recipes/")
    print("  2. Translate: python auto_translate_all.py")
    print("  3. Rebuild RAG: python recipe_rag_system.py")

def process_all_pdfs_in_folder():
    """Process all PDFs in pdf_cookbooks folder"""
    
    print("\n" + "="*70)
    print("BATCH PDF PROCESSOR")
    print("="*70 + "\n")
    
    pdf_folder = Path('pdf_cookbooks')
    if not pdf_folder.exists():
        print(f"❌ Folder not found: {pdf_folder}")
        print("Creating folder...")
        pdf_folder.mkdir(exist_ok=True)
        print(f"✅ Created: {pdf_folder}")
        print("\nPlease add your PDF files to this folder and run again")
        return
    
    pdfs = list(pdf_folder.glob('*.pdf'))
    
    if not pdfs:
        print(f"❌ No PDFs found in {pdf_folder}/")
        print("\nPlease add your PDF files and run again")
        return
    
    print(f"Found {len(pdfs)} PDFs:\n")
    for i, pdf in enumerate(pdfs, 1):
        print(f"  {i}. {pdf.name}")
    
    print("\nOptions:")
    print("  1. Process ALL PDFs (recommended)")
    print("  2. Select specific PDF")
    
    choice = input("\nSelect option (1-2): ").strip()
    
    if choice == "1":
        # Process all PDFs
        all_recipes = []
        current_id = 153
        
        # Get current recipe count
        db_path = Path('rag/data/recipes/recipe_database.json')
        if db_path.exists():
            with open(db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                current_id = data.get('total_recipes', 152) + 1
        
        for i, pdf_path in enumerate(pdfs, 1):
            print(f"\n{'='*70}")
            print(f"Processing PDF {i}/{len(pdfs)}: {pdf_path.name}")
            print('='*70)
            
            text = extract_text_from_pdf(str(pdf_path))
            if text:
                recipes = parse_recipes_from_text(text, start_id=current_id)
                all_recipes.extend(recipes)
                current_id += len(recipes)
        
        if all_recipes:
            save_extracted_recipes(all_recipes)
            print(f"\n{'='*70}")
            print(f"✅ BATCH PROCESSING COMPLETE")
            print(f"{'='*70}")
            print(f"\nExtracted {len(all_recipes)} recipes from {len(pdfs)} PDFs")
        
    else:
        # Single PDF selection
        pdf_num = input(f"\nEnter PDF number (1-{len(pdfs)}): ").strip()
        try:
            idx = int(pdf_num) - 1
            if 0 <= idx < len(pdfs):
                process_pdf_cookbook(str(pdfs[idx]))
        except ValueError:
            print("Invalid selection")

def main():
    """Main entry point"""
    
    print("\n" + "="*70)
    print("PDF COOKBOOK PROCESSOR")
    print("="*70)
    
    print("\nUsage:")
    print("  1. Place PDFs in: pdf_cookbooks/ folder")
    print("  2. Run this script")
    print("  3. Select processing option")
    
    print("\n📁 Checking for PDFs...")
    
    process_all_pdfs_in_folder()

if __name__ == "__main__":
    main()