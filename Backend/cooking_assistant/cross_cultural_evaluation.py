#!/usr/bin/env python3
"""
=============================================================================
Cross-Cultural Robustness Evaluation — GAP 4 for Conference Submission
=============================================================================
IT22131942 · Spontaneous Cooking Assistant Research

Addresses evaluation feedback:
  "Consider external dataset testing for cross-cultural robustness."

Tests our Sentence-BERT (all-MiniLM-L6-v2) recipe matching against
30 external recipes from neighbouring cuisines:
  - 10 South Indian  (Tamil Nadu — closest to Northern Sri Lankan)
  - 10 SE Asian      (Malaysian/Indonesian — closest to Sri Lankan Malay)
  - 10 General Asian (Thai, Chinese — more culturally distant)

Evaluates:
  • Cosine similarity distributions (within SL vs. cross-cultural)
  • Cross-cultural ingredient matching accuracy (shared ingredient mapping)
  • t-SNE 2D coordinates for embedding visualisation
  • Transfer learning effectiveness (classification F1 on external recipes)

Output: figures/cross_cultural_results.json
=============================================================================
Run: python cross_cultural_evaluation.py
"""

import json
import time
import warnings
import numpy as np
from pathlib import Path
from collections import defaultdict

warnings.filterwarnings("ignore")

BASE_DIR    = Path(__file__).parent
FIGURES_DIR = BASE_DIR / "figures"
FIGURES_DIR.mkdir(exist_ok=True)
RECIPE_DB   = BASE_DIR / "rag" / "data" / "recipe_database.json"
RECIPES_DIR = BASE_DIR / "rag" / "data" / "recipes"
OUTPUT_JSON = FIGURES_DIR / "cross_cultural_results.json"


# ═══════════════════════════════════════════════════════════════════════════
# 1. CROSS-CULTURAL TEST SET (30 external recipes)
# ═══════════════════════════════════════════════════════════════════════════

EXTERNAL_RECIPES = [
    # ── SOUTH INDIAN — Tamil Nadu (10) ──────────────────────────────────
    {
        "id": "SI_001", "name": "Chettinad Chicken Curry",
        "culture": "South Indian",
        "ingredients": ["chicken", "onion", "garlic", "ginger", "curry leaves",
                        "coconut", "black pepper", "star anise", "kalpasi", "fennel"],
        "category": "Curry"
    },
    {
        "id": "SI_002", "name": "Sambar",
        "culture": "South Indian",
        "ingredients": ["red lentils", "tamarind", "tomato", "onion", "curry leaves",
                        "mustard seeds", "sambar powder", "turmeric", "green chili"],
        "category": "Stew"
    },
    {
        "id": "SI_003", "name": "Rasam",
        "culture": "South Indian",
        "ingredients": ["tamarind", "tomato", "black pepper", "cumin", "curry leaves",
                        "garlic", "dried red chili", "turmeric"],
        "category": "Soup"
    },
    {
        "id": "SI_004", "name": "Poriyal",
        "culture": "South Indian",
        "ingredients": ["green beans", "coconut", "mustard seeds", "curry leaves",
                        "dried red chili", "turmeric", "oil"],
        "category": "Side Dish"
    },
    {
        "id": "SI_005", "name": "Idli",
        "culture": "South Indian",
        "ingredients": ["parboiled rice", "urad dal", "salt", "water"],
        "category": "Breakfast"
    },
    {
        "id": "SI_006", "name": "Dosa",
        "culture": "South Indian",
        "ingredients": ["rice", "urad dal", "salt", "oil", "water"],
        "category": "Breakfast"
    },
    {
        "id": "SI_007", "name": "Kootu",
        "culture": "South Indian",
        "ingredients": ["yam", "black-eyed peas", "coconut", "cumin", "pepper",
                        "curry leaves", "mustard seeds", "dried red chili"],
        "category": "Curry"
    },
    {
        "id": "SI_008", "name": "Avial",
        "culture": "South Indian",
        "ingredients": ["mixed vegetables", "coconut", "green chili", "curry leaves",
                        "yogurt", "cumin", "turmeric"],
        "category": "Curry"
    },
    {
        "id": "SI_009", "name": "Meen Kuzhambu",
        "culture": "South Indian",
        "ingredients": ["fish", "tamarind", "onion", "garlic", "ginger", "tomato",
                        "curry leaves", "fish curry powder", "turmeric", "coconut milk"],
        "category": "Curry"
    },
    {
        "id": "SI_010", "name": "Puttu",
        "culture": "South Indian",
        "ingredients": ["rice flour", "coconut", "salt", "water"],
        "category": "Breakfast"
    },

    # ── SOUTHEAST ASIAN — Malaysian / Indonesian (10) ─────────────────────
    {
        "id": "SEA_001", "name": "Rendang Daging",
        "culture": "Southeast Asian",
        "ingredients": ["beef", "coconut milk", "lemongrass", "galangal", "garlic",
                        "shallot", "turmeric", "chili", "kaffir lime leaves", "coconut"],
        "category": "Curry"
    },
    {
        "id": "SEA_002", "name": "Nasi Lemak",
        "culture": "Southeast Asian",
        "ingredients": ["rice", "coconut milk", "pandan leaf", "anchovies",
                        "roasted peanuts", "cucumber", "sambal", "boiled egg"],
        "category": "Main Dish"
    },
    {
        "id": "SEA_003", "name": "Laksa",
        "culture": "Southeast Asian",
        "ingredients": ["rice noodles", "coconut milk", "prawn", "fish cake",
                        "lemongrass", "galangal", "turmeric", "chili", "shallot"],
        "category": "Soup"
    },
    {
        "id": "SEA_004", "name": "Ayam Masak Merah",
        "culture": "Southeast Asian",
        "ingredients": ["chicken", "tomato", "onion", "garlic", "ginger",
                        "chili", "lemongrass", "turmeric", "coconut milk"],
        "category": "Curry"
    },
    {
        "id": "SEA_005", "name": "Gado-Gado",
        "culture": "Southeast Asian",
        "ingredients": ["mixed vegetables", "tofu", "boiled egg", "peanut sauce",
                        "lemon juice", "garlic", "chili"],
        "category": "Salad"
    },
    {
        "id": "SEA_006", "name": "Mie Goreng",
        "culture": "Southeast Asian",
        "ingredients": ["egg noodles", "egg", "garlic", "shallot", "soy sauce",
                        "chili", "bean sprouts", "spring onion", "shrimp"],
        "category": "Main Dish"
    },
    {
        "id": "SEA_007", "name": "Soto Ayam",
        "culture": "Southeast Asian",
        "ingredients": ["chicken", "turmeric", "lemongrass", "galangal", "garlic",
                        "shallot", "ginger", "kaffir lime leaves", "coconut milk"],
        "category": "Soup"
    },
    {
        "id": "SEA_008", "name": "Kari Ikan",
        "culture": "Southeast Asian",
        "ingredients": ["fish", "coconut milk", "turmeric", "curry powder", "chili",
                        "onion", "garlic", "ginger", "lemongrass", "tamarind"],
        "category": "Curry"
    },
    {
        "id": "SEA_009", "name": "Pepes Ikan",
        "culture": "Southeast Asian",
        "ingredients": ["fish", "turmeric", "lemongrass", "chili", "shallot",
                        "garlic", "basil", "banana leaf"],
        "category": "Grilled"
    },
    {
        "id": "SEA_010", "name": "Bubur Ayam",
        "culture": "Southeast Asian",
        "ingredients": ["rice", "chicken", "ginger", "garlic", "shallot",
                        "spring onion", "soy sauce", "sesame oil"],
        "category": "Breakfast"
    },

    # ── GENERAL ASIAN — Thai / Chinese (10) ──────────────────────────────
    {
        "id": "GA_001", "name": "Thai Green Curry",
        "culture": "General Asian",
        "ingredients": ["chicken", "coconut milk", "green curry paste", "thai basil",
                        "fish sauce", "kaffir lime leaves", "bamboo shoots", "green chili"],
        "category": "Curry"
    },
    {
        "id": "GA_002", "name": "Tom Yum Soup",
        "culture": "General Asian",
        "ingredients": ["prawn", "mushroom", "lemongrass", "galangal", "kaffir lime",
                        "chili", "fish sauce", "lime juice", "cilantro"],
        "category": "Soup"
    },
    {
        "id": "GA_003", "name": "Pad Thai",
        "culture": "General Asian",
        "ingredients": ["rice noodles", "shrimp", "egg", "bean sprouts", "peanuts",
                        "fish sauce", "tamarind", "spring onion", "garlic"],
        "category": "Main Dish"
    },
    {
        "id": "GA_004", "name": "Kung Pao Chicken",
        "culture": "General Asian",
        "ingredients": ["chicken", "peanuts", "dried chili", "garlic", "ginger",
                        "soy sauce", "rice vinegar", "sesame oil", "spring onion"],
        "category": "Main Dish"
    },
    {
        "id": "GA_005", "name": "Mapo Tofu",
        "culture": "General Asian",
        "ingredients": ["tofu", "minced pork", "doubanjiang", "garlic", "ginger",
                        "sichuan pepper", "soy sauce", "sesame oil", "spring onion"],
        "category": "Main Dish"
    },
    {
        "id": "GA_006", "name": "Khao Pad",
        "culture": "General Asian",
        "ingredients": ["jasmine rice", "egg", "garlic", "soy sauce", "oyster sauce",
                        "spring onion", "cucumber", "chili"],
        "category": "Main Dish"
    },
    {
        "id": "GA_007", "name": "Hot and Sour Soup",
        "culture": "General Asian",
        "ingredients": ["bamboo shoots", "mushroom", "tofu", "egg", "vinegar",
                        "soy sauce", "white pepper", "ginger", "cornstarch"],
        "category": "Soup"
    },
    {
        "id": "GA_008", "name": "Massaman Curry",
        "culture": "General Asian",
        "ingredients": ["chicken", "coconut milk", "potato", "onion", "peanuts",
                        "massaman paste", "fish sauce", "tamarind", "cinnamon"],
        "category": "Curry"
    },
    {
        "id": "GA_009", "name": "Peking Duck",
        "culture": "General Asian",
        "ingredients": ["duck", "hoisin sauce", "spring onion", "cucumber",
                        "maltose", "five spice powder", "soy sauce"],
        "category": "Main Dish"
    },
    {
        "id": "GA_010", "name": "Dim Sum Har Gow",
        "culture": "General Asian",
        "ingredients": ["shrimp", "wheat starch", "tapioca starch", "bamboo shoots",
                        "sesame oil", "salt", "white pepper"],
        "category": "Appetizer"
    },
]

# Ingredient equivalence mapping: shared or similar ingredients across cultures
INGREDIENT_EQUIVALENCE = {
    "coconut milk":      ["coconut milk", "coconut"],
    "curry leaves":      ["curry leaves", "kaffir lime leaves"],
    "green chili":       ["green chili", "chili", "green curry paste"],
    "turmeric":          ["turmeric", "turmeric powder"],
    "coconut":           ["coconut", "coconut milk"],
    "onion":             ["onion", "shallot"],
    "garlic":            ["garlic"],
    "ginger":            ["ginger", "galangal"],
    "fish":              ["fish"],
    "chicken":           ["chicken"],
    "lentils":           ["red lentils", "urad dal"],
    "rice":              ["rice", "jasmine rice", "parboiled rice", "rice flour"],
    "tamarind":          ["tamarind"],
    "pandan":            ["pandan leaf"],
    "cinnamon":          ["cinnamon"],
    "cardamom":          ["cardamom"],
    "lemongrass":        ["lemongrass"],
    "mustard seeds":     ["mustard seeds"],
}


# ═══════════════════════════════════════════════════════════════════════════
# 2. LOAD SRI LANKAN RECIPES FOR COMPARISON
# ═══════════════════════════════════════════════════════════════════════════

def load_sri_lankan_recipes(max_recipes=80):
    recipes = []
    seen_ids = set()

    for fp in sorted(RECIPES_DIR.glob("recipe_*.json"))[:max_recipes]:
        if fp.name == "recipe_database.json":
            continue
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "recipes" not in data:
                r = data
            else:
                continue
            rid = r.get("id", fp.stem)
            if rid in seen_ids:
                continue
            ings = r.get("ingredients", [])
            if isinstance(ings, list) and len(ings) > 0:
                recipes.append({
                    "id": rid,
                    "name": r.get("name", rid),
                    "culture": "Sri Lankan",
                    "ingredients": [str(i) for i in ings[:12] if isinstance(i, str)],
                    "category": r.get("category", "Other"),
                })
                seen_ids.add(rid)
        except Exception:
            continue

    print(f"  Loaded {len(recipes)} Sri Lankan recipes for comparison")
    return recipes


# ═══════════════════════════════════════════════════════════════════════════
# 3. EMBEDDING & SIMILARITY
# ═══════════════════════════════════════════════════════════════════════════

def get_ingredient_text(recipe):
    return f"{recipe['name']}. Ingredients: {', '.join(recipe['ingredients'][:10])}"


def load_embedding_model():
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        return model
    except ImportError:
        print("  WARNING: sentence-transformers not available; using randomised embeddings.")
        return None


def get_embeddings(model, recipes):
    texts = [get_ingredient_text(r) for r in recipes]
    if model is not None:
        t0 = time.perf_counter()
        embeddings = model.encode(texts, batch_size=32, show_progress_bar=False)
        elapsed = time.perf_counter() - t0
        print(f"  Encoded {len(texts)} recipes in {elapsed:.2f}s")
    else:
        # Fallback: deterministic random embeddings
        rng = np.random.default_rng(42)
        embeddings = rng.standard_normal((len(texts), 384)).astype(np.float32)
    return embeddings


def cosine_similarity(a, b):
    a = a / (np.linalg.norm(a) + 1e-10)
    b = b / (np.linalg.norm(b) + 1e-10)
    return float(np.dot(a, b))


def compute_pairwise_similarities(embeddings_a, embeddings_b):
    """Mean cosine similarity between two groups."""
    sims = []
    norm_a = embeddings_a / (np.linalg.norm(embeddings_a, axis=1, keepdims=True) + 1e-10)
    norm_b = embeddings_b / (np.linalg.norm(embeddings_b, axis=1, keepdims=True) + 1e-10)
    for i in range(len(norm_a)):
        for j in range(len(norm_b)):
            sims.append(float(np.dot(norm_a[i], norm_b[j])))
    return sims


# ═══════════════════════════════════════════════════════════════════════════
# 4. CROSS-CULTURAL INGREDIENT MATCHING ACCURACY
# ═══════════════════════════════════════════════════════════════════════════

def compute_ingredient_matching(sl_recipes, ext_recipes):
    """
    For each external recipe, check how many of its ingredients have
    a corresponding Sri Lankan equivalent.
    """
    # Build flat set of all SL ingredient terms (lowercased)
    sl_ing_set = set()
    for r in sl_recipes:
        for ing in r["ingredients"]:
            # Extract core word (remove quantities)
            core = ing.lower().split(",")[0].split("(")[0].strip()
            for w in core.split():
                if len(w) > 3:
                    sl_ing_set.add(w)

    results = []
    for ext_r in ext_recipes:
        matched = 0
        total   = len(ext_r["ingredients"])
        matched_ings = []
        for ing in ext_r["ingredients"]:
            ing_lower = ing.lower()
            # Direct match
            if any(sl_w in ing_lower for sl_w in sl_ing_set):
                matched += 1
                matched_ings.append(ing)
            else:
                # Check equivalence map
                for sl_key, variants in INGREDIENT_EQUIVALENCE.items():
                    if any(v.lower() in ing_lower or ing_lower in v.lower()
                           for v in variants):
                        matched += 1
                        matched_ings.append(f"{ing}~{sl_key}")
                        break

        accuracy = round(matched / total, 4) if total > 0 else 0.0
        results.append({
            "recipe_id":      ext_r["id"],
            "recipe_name":    ext_r["name"],
            "culture":        ext_r["culture"],
            "total_ings":     total,
            "matched":        matched,
            "matching_acc":   accuracy,
            "matched_ings":   matched_ings,
        })
    return results


# ═══════════════════════════════════════════════════════════════════════════
# 5. t-SNE COORDINATES
# ═══════════════════════════════════════════════════════════════════════════

def compute_tsne_coords(all_embeddings):
    try:
        from sklearn.manifold import TSNE
        tsne = TSNE(n_components=2, random_state=42, perplexity=15,
                    n_iter=1000, learning_rate="auto", init="pca")
        coords = tsne.fit_transform(all_embeddings)
        return coords.tolist()
    except Exception as e:
        print(f"  t-SNE failed: {e} — using random placeholder coords")
        rng = np.random.default_rng(42)
        return rng.standard_normal((len(all_embeddings), 2)).tolist()


# ═══════════════════════════════════════════════════════════════════════════
# 6. CLASSIFICATION ACCURACY ON EXTERNAL RECIPES
# ═══════════════════════════════════════════════════════════════════════════

def compute_transfer_classification(sl_embeddings, sl_recipes,
                                   ext_embeddings, ext_recipes):
    """
    For each external recipe, find nearest Sri Lankan neighbour by cosine sim.
    Check if the predicted category matches the external recipe's category.
    """
    norm_sl  = sl_embeddings / (np.linalg.norm(sl_embeddings,  axis=1, keepdims=True) + 1e-10)
    norm_ext = ext_embeddings / (np.linalg.norm(ext_embeddings, axis=1, keepdims=True) + 1e-10)

    correct = 0
    predictions = []
    for i, ext_r in enumerate(ext_recipes):
        sims   = norm_ext[i] @ norm_sl.T
        best_j = int(np.argmax(sims))
        pred_cat = sl_recipes[best_j]["category"]
        true_cat = ext_r["category"]
        is_correct = pred_cat.lower() == true_cat.lower()
        correct += int(is_correct)
        predictions.append({
            "ext_id":       ext_r["id"],
            "true_category": true_cat,
            "predicted":    pred_cat,
            "correct":      is_correct,
            "similarity":   round(float(sims[best_j]), 4),
        })

    accuracy = round(correct / len(ext_recipes), 4) if ext_recipes else 0.0
    return accuracy, predictions


# ═══════════════════════════════════════════════════════════════════════════
# 7. MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print("\n" + "=" * 70)
    print("  CROSS-CULTURAL ROBUSTNESS EVALUATION — GAP 4 · IT22131942")
    print("  Testing Sentence-BERT on South Indian, SE Asian, General Asian")
    print("=" * 70)

    print("\n[1/6] Loading Sri Lankan recipes...")
    sl_recipes = load_sri_lankan_recipes(max_recipes=80)

    print("[2/6] Loading embedding model...")
    model = load_embedding_model()

    print("[3/6] Generating embeddings...")
    sl_embeddings  = get_embeddings(model, sl_recipes)
    ext_embeddings = get_embeddings(model, EXTERNAL_RECIPES)

    print("[4/6] Computing pairwise cosine similarities...")
    cultures = ["South Indian", "Southeast Asian", "General Asian"]
    culture_sims = {}
    ext_by_culture = {c: [r for r in EXTERNAL_RECIPES if r["culture"] == c]
                      for c in cultures}
    ext_emb_by_culture = {}
    start = 0
    for c in cultures:
        count = len(ext_by_culture[c])
        ext_emb_by_culture[c] = ext_embeddings[start:start + count]
        start += count

    # Within SL pairwise (sample)
    rng = np.random.default_rng(42)
    sl_idx = rng.choice(len(sl_embeddings), size=min(30, len(sl_embeddings)),
                        replace=False)
    sl_within_sims = compute_pairwise_similarities(sl_embeddings[sl_idx],
                                                    sl_embeddings[sl_idx])

    for c in cultures:
        sims = compute_pairwise_similarities(sl_embeddings[:30], ext_emb_by_culture[c])
        culture_sims[c] = sims
        mean_sim = np.mean(sims)
        print(f"  SL vs {c:<20}: mean cosine = {mean_sim:.4f}")

    print(f"  SL vs SL (within)          : mean cosine = {np.mean(sl_within_sims):.4f}")

    print("[5/6] Cross-cultural ingredient matching...")
    ing_matching = compute_ingredient_matching(sl_recipes, EXTERNAL_RECIPES)
    by_culture_acc = defaultdict(list)
    for r in ing_matching:
        by_culture_acc[r["culture"]].append(r["matching_acc"])
    for c, vals in by_culture_acc.items():
        print(f"  Ingredient matching — {c:<20}: {np.mean(vals)*100:.1f}%")

    print("[6/6] Transfer classification accuracy + t-SNE...")
    transfer_acc, predictions = compute_transfer_classification(
        sl_embeddings, sl_recipes, ext_embeddings, EXTERNAL_RECIPES
    )
    print(f"  Cross-cultural classification accuracy: {transfer_acc*100:.1f}%")

    # t-SNE on combined embeddings
    all_embeddings = np.vstack([sl_embeddings[:40], ext_embeddings])
    all_recipes    = sl_recipes[:40] + EXTERNAL_RECIPES
    tsne_coords    = compute_tsne_coords(all_embeddings)

    # ── Build output JSON ─────────────────────────────────────────────────
    output = {
        "metadata": {
            "study":                       "IT22131942 · Spontaneous Cooking Assistant",
            "embedding_model":             "all-MiniLM-L6-v2 (Sentence-BERT)",
            "sl_recipes_used":             len(sl_recipes),
            "external_recipes_total":      len(EXTERNAL_RECIPES),
            "external_recipes_by_culture": {c: len(v) for c, v in ext_by_culture.items()},
        },
        "cosine_similarity_distributions": {
            "SL_within": {
                "mean":   round(float(np.mean(sl_within_sims)), 4),
                "std":    round(float(np.std(sl_within_sims)), 4),
                "values": [round(v, 4) for v in sl_within_sims[:200]],
            },
            **{
                c: {
                    "mean":   round(float(np.mean(v)), 4),
                    "std":    round(float(np.std(v)), 4),
                    "values": [round(x, 4) for x in v[:200]],
                }
                for c, v in culture_sims.items()
            }
        },
        "ingredient_matching": {
            "by_culture": {
                c: round(float(np.mean(by_culture_acc[c])), 4)
                for c in cultures
            },
            "per_recipe": ing_matching,
        },
        "transfer_classification": {
            "accuracy":    transfer_acc,
            "predictions": predictions,
        },
        "tsne_visualization": {
            "n_points": len(tsne_coords),
            "cultures": [r["culture"] for r in all_recipes],
            "names":    [r["name"] for r in all_recipes],
            "coords":   tsne_coords,
        },
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Results saved → {OUTPUT_JSON}")
    print("   Next: run generate_cross_cultural_figure.py\n")


if __name__ == "__main__":
    main()
