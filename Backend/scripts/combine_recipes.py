"""Combine all 4 recipe JSON parts into a single new_200_recipes.json"""
import json, os

script_dir = os.path.dirname(os.path.abspath(__file__))
all_recipes = []
for part in ["generate_recipes_data_p1.json","generate_recipes_data_p2.json","generate_recipes_data_p3.json","generate_recipes_data_p4.json"]:
    fp = os.path.join(script_dir, part)
    with open(fp, "r", encoding="utf-8") as f:
        recipes = json.load(f)
        all_recipes.extend(recipes)
        print(f"  Loaded {len(recipes)} from {part}")

# Validate
assert len(all_recipes) == 200, f"Expected 200 recipes, got {len(all_recipes)}"
ids = [r["id"] for r in all_recipes]
assert len(set(ids)) == 200, "Duplicate IDs found!"
assert ids[0] == "SL_0191" and ids[-1] == "SL_0390", "ID range mismatch"

# Category distribution
cats = {}
for r in all_recipes:
    cats[r["category"]] = cats.get(r["category"], 0) + 1
print(f"\nTotal: {len(all_recipes)} recipes")
print("Category distribution:")
for cat, count in sorted(cats.items()):
    print(f"  {cat}: {count}")

# Save to rag/data
output_path = os.path.join(script_dir, "..", "cooking_assistant", "rag", "data", "new_200_recipes.json")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_recipes, f, indent=2, ensure_ascii=False)
print(f"\nSaved to: {os.path.abspath(output_path)}")
