"""
Merge Script: Combine existing recipes with new translated recipes
Deduplicates, normalizes formats, and outputs merged database
"""
import json
import os
import glob

def normalize_recipe(recipe):
    """Normalize recipe to standard english/sinhala/tamil format"""
    normalized = {}
    
    # Handle different ID formats
    rid = recipe.get("id", "")
    if not str(rid).startswith("SL_"):
        rid = f"SL_{int(rid):04d}" if str(rid).isdigit() else rid
    normalized["id"] = rid
    
    # Handle names - multiple possible formats
    if "names" in recipe:
        names = recipe["names"]
        normalized["names"] = {
            "english": names.get("english", names.get("en", "")),
            "sinhala": names.get("sinhala", names.get("si", "")),
            "tamil": names.get("tamil", names.get("ta", ""))
        }
    elif "name" in recipe:
        name = recipe["name"]
        if isinstance(name, dict):
            normalized["names"] = {
                "english": name.get("english", name.get("en", "")),
                "sinhala": name.get("sinhala", name.get("si", "")),
                "tamil": name.get("tamil", name.get("ta", ""))
            }
        else:
            normalized["names"] = {"english": str(name), "sinhala": "", "tamil": ""}
    
    # Category
    cat = recipe.get("category", recipe.get("meal_type", "other"))
    if isinstance(cat, dict):
        cat = cat.get("english", "other")
    normalized["category"] = cat.lower() if isinstance(cat, str) else "other"
    
    # Difficulty
    diff = recipe.get("difficulty", "medium")
    if isinstance(diff, dict):
        diff = diff.get("english", "medium")
    normalized["difficulty"] = diff.lower() if isinstance(diff, str) else "medium"
    
    # Times and servings
    normalized["prep_time_mins"] = recipe.get("prep_time_mins", recipe.get("prep_time", 15))
    normalized["cook_time_mins"] = recipe.get("cook_time_mins", recipe.get("cook_time", 30))
    normalized["servings"] = recipe.get("servings", 4)
    
    # Region
    region = recipe.get("region", "Island-wide")
    if isinstance(region, dict):
        region = region.get("english", "Island-wide")
    normalized["region"] = region
    
    normalized["spice_level"] = recipe.get("spice_level", 2)
    normalized["is_authentic"] = recipe.get("is_authentic", True)
    
    # Ingredients - normalize to list of {name, amount} with optional translations
    raw_ings = recipe.get("ingredients", [])
    norm_ings = []
    if isinstance(raw_ings, list):
        for ing in raw_ings:
            if isinstance(ing, dict):
                ni = {"name": ing.get("name", ing.get("item", "")), "amount": ing.get("amount", "")}
                if isinstance(ni["name"], dict):
                    ni["name"] = ni["name"].get("english", "")
                if "names" in ing:
                    ni["names"] = ing["names"]
                norm_ings.append(ni)
            elif isinstance(ing, str):
                norm_ings.append({"name": ing, "amount": ""})
    elif isinstance(raw_ings, dict):
        en_list = raw_ings.get("en", raw_ings.get("english", []))
        for item in en_list:
            norm_ings.append({"name": item, "amount": ""})
    normalized["ingredients"] = norm_ings
    
    # Method
    method = recipe.get("method", recipe.get("instructions", ""))
    if isinstance(method, dict):
        method = method.get("english", method.get("en", ""))
    if isinstance(method, list):
        method = "\n".join(f"{i+1}. {s}" for i, s in enumerate(method))
    normalized["method"] = method
    
    # Tips
    tips = recipe.get("tips", "")
    if isinstance(tips, dict):
        tips = tips.get("english", "")
    if isinstance(tips, list):
        tips = ". ".join(tips)
    normalized["tips"] = tips
    
    # Cultural note
    cn = recipe.get("cultural_note", "")
    if isinstance(cn, dict):
        cn = cn.get("english", "")
    normalized["cultural_note"] = cn
    
    # Preserve translations if present
    for field in ["method_translations", "tips_translations", "cultural_note_translations"]:
        if field in recipe:
            normalized[field] = recipe[field]
    
    return normalized

def get_recipe_name(recipe):
    """Get English name from recipe in any format"""
    if "names" in recipe:
        n = recipe["names"]
        return (n.get("english", n.get("en", ""))).strip().lower()
    elif "name" in recipe:
        n = recipe["name"]
        if isinstance(n, dict):
            return (n.get("english", n.get("en", ""))).strip().lower()
        return str(n).strip().lower()
    return ""

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "cooking_assistant", "rag", "data")
    
    all_recipes = []
    seen_names = set()
    
    # 1. Load existing recipe_database.json
    db_path = os.path.join(data_dir, "recipe_database.json")
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        recipes = data.get("recipes", data) if isinstance(data, dict) else data
        if isinstance(recipes, list):
            for r in recipes:
                name = get_recipe_name(r)
                if name and name not in seen_names:
                    all_recipes.append(normalize_recipe(r))
                    seen_names.add(name)
            print(f"Loaded {len(recipes)} from recipe_database.json ({len(seen_names)} unique)")
    
    # 2. Load individual recipe JSON files
    recipes_dir = os.path.join(data_dir, "recipes")
    if os.path.exists(recipes_dir):
        count_before = len(all_recipes)
        for fp in sorted(glob.glob(os.path.join(recipes_dir, "recipe_*.json"))):
            if fp.endswith("recipe_database.json"):
                continue
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    r = json.load(f)
                name = get_recipe_name(r)
                if name and name not in seen_names:
                    all_recipes.append(normalize_recipe(r))
                    seen_names.add(name)
            except Exception as e:
                print(f"  Warning: could not load {fp}: {e}")
        print(f"Loaded {len(all_recipes)-count_before} unique from individual recipe files")
    
    # 3. Load new translated recipes
    translated_path = os.path.join(data_dir, "recipes_200_translated.json")
    new_path = os.path.join(data_dir, "new_200_recipes.json")
    source = translated_path if os.path.exists(translated_path) else new_path
    
    if os.path.exists(source):
        with open(source, "r", encoding="utf-8") as f:
            new_recipes = json.load(f)
        count_before = len(all_recipes)
        dupes = 0
        for r in new_recipes:
            name = get_recipe_name(r)
            if name and name not in seen_names:
                all_recipes.append(normalize_recipe(r))
                seen_names.add(name)
            else:
                dupes += 1
        print(f"Loaded {len(all_recipes)-count_before} new recipes from {os.path.basename(source)} ({dupes} duplicates skipped)")
    
    # 4. Reassign sequential IDs
    for i, recipe in enumerate(all_recipes):
        recipe["id"] = f"SL_{i+1:04d}"
    
    # 5. Statistics
    cats = {}
    regions = {}
    for r in all_recipes:
        c = r.get("category", "other")
        cats[c] = cats.get(c, 0) + 1
        reg = r.get("region", "Unknown")
        regions[reg] = regions.get(reg, 0) + 1
    
    print(f"\n{'='*50}")
    print(f"MERGED DATABASE STATISTICS")
    print(f"{'='*50}")
    print(f"Total recipes: {len(all_recipes)}")
    print(f"\nBy Category:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
    print(f"\nBy Region:")
    for reg, count in sorted(regions.items(), key=lambda x: -x[1]):
        print(f"  {reg}: {count}")
    
    has_si = sum(1 for r in all_recipes if r["names"].get("sinhala"))
    has_ta = sum(1 for r in all_recipes if r["names"].get("tamil"))
    print(f"\nLanguages:")
    print(f"  English: {len(all_recipes)}")
    print(f"  Sinhala: {has_si}")
    print(f"  Tamil: {has_ta}")
    
    # 6. Save merged database
    output_path = os.path.join(data_dir, "recipes_all_merged.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_recipes, f, indent=2, ensure_ascii=False)
    print(f"\nSaved merged database to: {output_path}")

if __name__ == "__main__":
    main()
