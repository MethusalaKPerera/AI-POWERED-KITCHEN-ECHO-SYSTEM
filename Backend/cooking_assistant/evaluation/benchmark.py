"""
Comparative Evaluation Benchmark
=================================
Compares 3 recipe search methods on the same test set:
  1. Keyword matching  (from routes.py)
  2. TF-IDF + cosine similarity  (classical NLP baseline)
  3. Sentence-BERT semantic search  (from sbert_matcher.py)

Metrics computed:
  - Precision@K
  - Recall@K
  - NDCG@K
  - Mean Reciprocal Rank (MRR)

Run:
  cd Backend/cooking_assistant
  python -m evaluation.benchmark
"""

import os, sys, json, time, math
import numpy as np
from pathlib import Path

# ── ensure cooking_assistant is on path ───────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# ══════════════════════════════════════════════════════════════════════════════
#  GROUND-TRUTH TEST QUERIES
#  Each query has: ingredients the user provides, and the expected recipe names
#  (case-insensitive partial match is accepted)
# ══════════════════════════════════════════════════════════════════════════════

TEST_QUERIES = [
    {
        "id": "Q01",
        "ingredients": ["chicken", "onion", "coconut milk", "curry powder"],
        "relevant_recipes": ["chicken curry", "kukul mas"],
        "description": "Classic chicken curry ingredients"
    },
    {
        "id": "Q02",
        "ingredients": ["fish", "tomato", "chili", "goraka", "onion"],
        "relevant_recipes": ["fish curry", "malu curry", "ambulthiyal"],
        "description": "Fish curry with goraka"
    },
    {
        "id": "Q03",
        "ingredients": ["lentil", "coconut milk", "turmeric", "onion"],
        "relevant_recipes": ["dhal", "parippu", "lentil curry", "dhal curry"],
        "description": "Dhal / lentil curry"
    },
    {
        "id": "Q04",
        "ingredients": ["egg", "onion", "chili", "curry leaves"],
        "relevant_recipes": ["egg curry", "bittara", "egg"],
        "description": "Egg-based dishes"
    },
    {
        "id": "Q05",
        "ingredients": ["rice", "chicken", "onion", "garlic", "soy sauce"],
        "relevant_recipes": ["fried rice", "chicken fried rice", "nasi goreng"],
        "description": "Fried rice"
    },
    {
        "id": "Q06",
        "ingredients": ["coconut", "chili", "onion", "lime", "maldive fish"],
        "relevant_recipes": ["pol sambol", "coconut sambol", "sambol"],
        "description": "Coconut sambol"
    },
    {
        "id": "Q07",
        "ingredients": ["prawn", "onion", "garlic", "curry powder", "coconut milk"],
        "relevant_recipes": ["prawn curry", "isso", "shrimp curry"],
        "description": "Prawn / shrimp curry"
    },
    {
        "id": "Q08",
        "ingredients": ["flour", "coconut milk", "egg", "sugar"],
        "relevant_recipes": ["hopper", "appa", "string hopper", "pancake"],
        "description": "Hopper / appa"
    },
    {
        "id": "Q09",
        "ingredients": ["potato", "onion", "curry powder", "turmeric"],
        "relevant_recipes": ["potato curry", "ala curry", "potato"],
        "description": "Potato curry"
    },
    {
        "id": "Q10",
        "ingredients": ["jackfruit", "coconut milk", "onion", "curry powder"],
        "relevant_recipes": ["jackfruit curry", "polos", "kos"],
        "description": "Jackfruit curry"
    },
    {
        "id": "Q11",
        "ingredients": ["beef", "onion", "curry powder", "coconut milk", "cinnamon"],
        "relevant_recipes": ["beef curry", "beef", "haraka mas"],
        "description": "Beef curry"
    },
    {
        "id": "Q12",
        "ingredients": ["eggplant", "onion", "chili", "coconut"],
        "relevant_recipes": ["eggplant", "brinjal", "wambatu"],
        "description": "Eggplant / brinjal curry"
    },
    {
        "id": "Q13",
        "ingredients": ["rice", "coconut milk", "pandan"],
        "relevant_recipes": ["coconut rice", "kiri bath", "yellow rice"],
        "description": "Coconut or yellow rice"
    },
    {
        "id": "Q14",
        "ingredients": ["mutton", "onion", "garlic", "ginger", "curry powder"],
        "relevant_recipes": ["mutton curry", "lamb curry", "mutton"],
        "description": "Mutton / lamb curry"
    },
    {
        "id": "Q15",
        "ingredients": ["flour", "coconut", "sugar", "cardamom"],
        "relevant_recipes": ["kokis", "kavum", "aluwa", "dessert", "sweet"],
        "description": "Traditional Sri Lankan sweets"
    },
    {
        "id": "Q16",
        "ingredients": ["crab", "onion", "chili", "curry powder", "coconut milk"],
        "relevant_recipes": ["crab curry", "kakuluwo"],
        "description": "Crab curry"
    },
    {
        "id": "Q17",
        "ingredients": ["beetroot", "coconut", "onion", "curry leaves"],
        "relevant_recipes": ["beetroot", "beetroot curry"],
        "description": "Beetroot curry"
    },
    {
        "id": "Q18",
        "ingredients": ["pumpkin", "coconut milk", "onion", "turmeric"],
        "relevant_recipes": ["pumpkin curry", "wattakka"],
        "description": "Pumpkin curry"
    },
    {
        "id": "Q19",
        "ingredients": ["onion", "chili", "lime", "maldive fish", "tomato"],
        "relevant_recipes": ["lunu miris", "seeni sambol", "sambol"],
        "description": "Lunu miris / seeni sambol"
    },
    {
        "id": "Q20",
        "ingredients": ["spinach", "garlic", "onion", "coconut milk"],
        "relevant_recipes": ["spinach", "nivithi", "green leaves", "mallung"],
        "description": "Spinach / green leaf curry"
    },
]


# ══════════════════════════════════════════════════════════════════════════════
#  HELPER: Load recipe database
# ══════════════════════════════════════════════════════════════════════════════

def load_recipes():
    """Load recipes the same way routes.py does."""
    data_dir = BASE_DIR / 'rag' / 'data'
    for fname in ['recipes_all_merged.json', 'new_200_recipes.json', 'recipe_database.json']:
        fp = data_dir / fname
        if fp.exists():
            with open(fp, 'r', encoding='utf-8') as f:
                data = json.load(f)
            recipes = data.get('recipes', []) if isinstance(data, dict) else data
            print(f"[benchmark] Loaded {len(recipes)} recipes from {fname}")
            return recipes
    print("[benchmark] ERROR: No recipe database found!")
    return []


def get_recipe_name(recipe):
    names = recipe.get('names', {})
    if isinstance(names, dict):
        en = names.get('english', '') or names.get('en', '')
    else:
        en = str(names) if names else ''
    return en or recipe.get('name', 'Unknown Recipe')


# ══════════════════════════════════════════════════════════════════════════════
#  METHOD 1: Keyword Matching (reuse from routes.py)
# ══════════════════════════════════════════════════════════════════════════════

def keyword_search(user_ingredients, recipes, top_k=10):
    """Import and use the existing keyword search from routes.py."""
    from routes import _keyword_search
    return _keyword_search(user_ingredients, recipes, top_k=top_k)


# ══════════════════════════════════════════════════════════════════════════════
#  METHOD 2: TF-IDF + Cosine Similarity
# ══════════════════════════════════════════════════════════════════════════════

def tfidf_search(user_ingredients, recipes, top_k=10):
    """Classical TF-IDF approach for recipe retrieval."""
    import re
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    # Build recipe texts
    recipe_texts = []
    valid_recipes = []
    for recipe in recipes:
        name = get_recipe_name(recipe)
        ings = []
        for ing in recipe.get('ingredients', []):
            if isinstance(ing, dict):
                ing_name = ing.get('name', '')
                if isinstance(ing_name, dict):
                    ing_name = ing_name.get('english', '')
            else:
                ing_name = str(ing)
            ing_name = re.sub(
                r'^\d[\d./]*\s*(g|kg|ml|l|cup|tsp|tbsp|oz|lb|piece|pieces)?\s*',
                '', ing_name.strip(), flags=re.IGNORECASE
            ).strip().lower()
            if ing_name and "ingredients to be added" not in ing_name.lower():
                ings.append(ing_name)

        method = recipe.get('method', '') or recipe.get('instructions', '')
        if not method or "instructions to be added" in str(method).lower():
            continue
        if not ings:
            continue

        cat = recipe.get('category', '')
        text = f"{name}. Category: {cat}. Ingredients: {', '.join(ings)}"
        recipe_texts.append(text)
        valid_recipes.append(recipe)

    if not recipe_texts:
        return []

    # Build query text
    query_text = f"Available ingredients: {', '.join(user_ingredients)}"

    # TF-IDF vectorize
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    all_texts = recipe_texts + [query_text]
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    query_vec = tfidf_matrix[-1]
    recipe_vecs = tfidf_matrix[:-1]

    # Cosine similarity
    sims = cosine_similarity(query_vec, recipe_vecs).flatten()

    # Build results
    results = []
    for i, sim_score in enumerate(sims):
        if sim_score < 0.01:
            continue
        recipe = valid_recipes[i]
        en_name = get_recipe_name(recipe)
        match_score = max(0, min(100, round(sim_score * 100)))

        cook_mins = recipe.get('cook_time_mins', recipe.get('cook_time_minutes', 30))
        prep_mins = recipe.get('prep_time_mins', recipe.get('prep_time_minutes', 10))

        results.append({
            'id': recipe.get('id', ''),
            'name': en_name,
            'match_score': match_score,
            'search_method': 'tfidf',
        })

    results.sort(key=lambda x: x['match_score'], reverse=True)
    return results[:top_k]


# ══════════════════════════════════════════════════════════════════════════════
#  METHOD 3: SBERT Semantic Search (reuse from sbert_matcher.py)
# ══════════════════════════════════════════════════════════════════════════════

def sbert_search(user_ingredients, recipes, top_k=10):
    """Import and use the existing SBERT search."""
    from sbert_matcher import sbert_search_recipes
    return sbert_search_recipes(user_ingredients, recipes, top_k=top_k)


# ══════════════════════════════════════════════════════════════════════════════
#  IR METRICS
# ══════════════════════════════════════════════════════════════════════════════

def is_relevant(result_name, relevant_names):
    """Check if a result is relevant based on partial name matching."""
    name_lower = result_name.lower()
    for rel in relevant_names:
        if rel.lower() in name_lower or name_lower in rel.lower():
            return True
        # word-level match
        for word in rel.lower().split():
            if len(word) >= 3 and word in name_lower:
                return True
    return False


def precision_at_k(results, relevant_names, k=5):
    """Precision@K: fraction of top-K results that are relevant."""
    top_k = results[:k]
    if not top_k:
        return 0.0
    relevant_count = sum(1 for r in top_k if is_relevant(r.get('name', ''), relevant_names))
    return relevant_count / len(top_k)


def recall_at_k(results, relevant_names, k=5):
    """Recall@K: fraction of relevant recipes found in top-K."""
    if not relevant_names:
        return 0.0
    top_k = results[:k]
    found = sum(1 for rel in relevant_names
                if any(is_relevant(r.get('name', ''), [rel]) for r in top_k))
    return found / len(relevant_names)


def reciprocal_rank(results, relevant_names):
    """Reciprocal Rank: 1/rank of the first relevant result."""
    for i, r in enumerate(results):
        if is_relevant(r.get('name', ''), relevant_names):
            return 1.0 / (i + 1)
    return 0.0


def dcg_at_k(results, relevant_names, k=5):
    """Discounted Cumulative Gain at K."""
    dcg = 0.0
    for i, r in enumerate(results[:k]):
        rel = 1.0 if is_relevant(r.get('name', ''), relevant_names) else 0.0
        dcg += rel / math.log2(i + 2)  # i+2 because log2(1) = 0
    return dcg


def ndcg_at_k(results, relevant_names, k=5):
    """Normalized DCG at K."""
    dcg = dcg_at_k(results, relevant_names, k)
    # Ideal DCG: all relevant docs at the top
    ideal_rels = min(len(relevant_names), k)
    idcg = sum(1.0 / math.log2(i + 2) for i in range(ideal_rels))
    if idcg == 0:
        return 0.0
    return dcg / idcg


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN BENCHMARK
# ══════════════════════════════════════════════════════════════════════════════

def run_benchmark(k=5):
    """Run all three methods on all test queries and compute metrics."""
    recipes = load_recipes()
    if not recipes:
        print("ERROR: No recipes to evaluate!")
        return

    methods = {
        'Keyword Matching': keyword_search,
        'TF-IDF Cosine': tfidf_search,
        'SBERT Semantic': sbert_search,
    }

    all_results = {name: [] for name in methods}
    query_details = []

    print(f"\n{'='*80}")
    print(f"  COMPARATIVE EVALUATION BENCHMARK  (K={k})")
    print(f"  {len(TEST_QUERIES)} test queries · {len(recipes)} recipes · 3 methods")
    print(f"{'='*80}\n")

    for q in TEST_QUERIES:
        qid = q['id']
        ings = q['ingredients']
        relevant = q['relevant_recipes']
        desc = q['description']

        print(f"  {qid}: {desc}")
        print(f"       Ingredients: {', '.join(ings)}")

        query_detail = {'id': qid, 'description': desc, 'ingredients': ings, 'methods': {}}

        for method_name, search_fn in methods.items():
            try:
                t0 = time.time()
                results = search_fn(ings, recipes, top_k=k)
                elapsed = time.time() - t0

                p_at_k = precision_at_k(results, relevant, k)
                r_at_k = recall_at_k(results, relevant, k)
                rr = reciprocal_rank(results, relevant)
                ndcg = ndcg_at_k(results, relevant, k)

                all_results[method_name].append({
                    'precision': p_at_k,
                    'recall': r_at_k,
                    'mrr': rr,
                    'ndcg': ndcg,
                    'time': elapsed,
                    'n_results': len(results),
                })

                top_names = [r.get('name', '?')[:40] for r in results[:3]]
                print(f"       {method_name:20s} P@{k}={p_at_k:.2f}  R@{k}={r_at_k:.2f}  MRR={rr:.2f}  NDCG={ndcg:.2f}  ({elapsed:.3f}s)")

                query_detail['methods'][method_name] = {
                    'precision': round(p_at_k, 4),
                    'recall': round(r_at_k, 4),
                    'mrr': round(rr, 4),
                    'ndcg': round(ndcg, 4),
                    'time_seconds': round(elapsed, 4),
                    'top_3_results': top_names,
                }

            except Exception as e:
                print(f"       {method_name:20s} ERROR: {e}")
                all_results[method_name].append({
                    'precision': 0, 'recall': 0, 'mrr': 0, 'ndcg': 0, 'time': 0, 'n_results': 0
                })
                query_detail['methods'][method_name] = {'error': str(e)}

        query_details.append(query_detail)
        print()

    # ── Aggregate results ──────────────────────────────────────────────────────
    print(f"\n{'='*80}")
    print(f"  AGGREGATE RESULTS  (averaged over {len(TEST_QUERIES)} queries, K={k})")
    print(f"{'='*80}\n")

    header = f"  {'Method':22s} {'Precision@'+str(k):>12s} {'Recall@'+str(k):>10s} {'MRR':>8s} {'NDCG@'+str(k):>10s} {'Avg Time':>10s}"
    print(header)
    print("  " + "-" * (len(header) - 2))

    summary = {}
    for method_name in methods:
        vals = all_results[method_name]
        avg_p = np.mean([v['precision'] for v in vals])
        avg_r = np.mean([v['recall'] for v in vals])
        avg_mrr = np.mean([v['mrr'] for v in vals])
        avg_ndcg = np.mean([v['ndcg'] for v in vals])
        avg_time = np.mean([v['time'] for v in vals])

        print(f"  {method_name:22s} {avg_p:12.4f} {avg_r:10.4f} {avg_mrr:8.4f} {avg_ndcg:10.4f} {avg_time:9.4f}s")

        summary[method_name] = {
            'precision_at_k': round(avg_p, 4),
            'recall_at_k': round(avg_r, 4),
            'mrr': round(avg_mrr, 4),
            'ndcg_at_k': round(avg_ndcg, 4),
            'avg_time_seconds': round(avg_time, 4),
        }

    print()

    # ── Find best method ───────────────────────────────────────────────────────
    best_method = max(summary, key=lambda m: summary[m]['ndcg_at_k'])
    print(f"  Best method by NDCG@{k}: {best_method}")
    print()

    # ── Save results ───────────────────────────────────────────────────────────
    output_dir = Path(__file__).parent
    results_file = output_dir / 'results.json'

    output = {
        'config': {
            'k': k,
            'n_queries': len(TEST_QUERIES),
            'n_recipes': len(recipes),
            'methods': list(methods.keys()),
        },
        'summary': summary,
        'best_method': best_method,
        'query_details': query_details,
    }

    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"  Results saved to: {results_file}")

    # ── Generate chart ─────────────────────────────────────────────────────────
    try:
        generate_chart(summary, k, output_dir)
    except Exception as e:
        print(f"  Warning: Could not generate chart: {e}")

    return output


def generate_chart(summary, k, output_dir):
    """Generate a comparison bar chart."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    methods = list(summary.keys())
    metrics = [f'Precision@{k}', f'Recall@{k}', 'MRR', f'NDCG@{k}']
    metric_keys = ['precision_at_k', 'recall_at_k', 'mrr', 'ndcg_at_k']

    x = np.arange(len(metrics))
    width = 0.22
    colors = ['#6366f1', '#f59e0b', '#10b981']

    fig, ax = plt.subplots(figsize=(12, 6))

    for i, method in enumerate(methods):
        values = [summary[method][mk] for mk in metric_keys]
        bars = ax.bar(x + i * width, values, width, label=method, color=colors[i],
                      edgecolor='white', linewidth=0.5)
        # Add value labels on bars
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.01,
                    f'{val:.3f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

    ax.set_xlabel('Metrics', fontsize=12, fontweight='bold')
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title(f'Recipe Search Method Comparison (K={k}, {len(TEST_QUERIES)} queries)',
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(x + width)
    ax.set_xticklabels(metrics, fontsize=11)
    ax.set_ylim(0, 1.15)
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    chart_path = output_dir / 'comparison_chart.png'
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Chart saved to: {chart_path}")


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    run_benchmark(k=5)
