#!/usr/bin/env python3
"""
PP1 (Progress Presentation 1) Preparation Tool
Generates statistics, metrics, and documentation for your research presentation
For AI-Powered Kitchen Echo System
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np


class PP1Preparation:
    """Generate PP1 presentation materials"""
    
    def __init__(self, project_dir: str = '.'):
        self.project_dir = Path(project_dir)
        self.rag_dir = self.project_dir / 'rag' / 'data'
        self.output_dir = self.project_dir / 'pp1_materials'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'='*70}")
        print("STATS PP1 PREPARATION TOOL")
        print(f"{'='*70}\n")
    
    def load_data(self):
        """Load all necessary data"""
        
        # Load recipe database
        recipe_db_path = self.rag_dir / 'recipes' / 'recipe_database.json'
        with open(recipe_db_path, 'r', encoding='utf-8') as f:
            self.recipe_data = json.load(f)
        
        # Load ingredient database
        ingredient_db_path = self.rag_dir / 'ingredient_database.json'
        with open(ingredient_db_path, 'r', encoding='utf-8') as f:
            self.ingredient_data = json.load(f)
        
        # Load evaluation metrics if exists
        metrics_path = self.rag_dir / 'embeddings' / 'evaluation_metrics.json'
        if metrics_path.exists():
            with open(metrics_path, 'r') as f:
                self.eval_metrics = json.load(f)
        else:
            self.eval_metrics = None
        
        print(f"OK Loaded {len(self.recipe_data['recipes'])} recipes")
        print(f"OK Loaded {self.ingredient_data['total_ingredients']} ingredients")
    
    def generate_dataset_statistics(self) -> Dict:
        """Generate comprehensive dataset statistics"""
        
        recipes = self.recipe_data['recipes']
        
        # Category distribution
        categories = {}
        for recipe in recipes:
            cat = recipe['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        # Difficulty distribution
        difficulties = {}
        for recipe in recipes:
            diff = recipe['difficulty']
            difficulties[diff] = difficulties.get(diff, 0) + 1
        
        # Time statistics
        prep_times = [r['prep_time_minutes'] for r in recipes if r.get('prep_time_minutes')]
        cook_times = [r['cook_time_minutes'] for r in recipes if r.get('cook_time_minutes')]
        total_times = [p + c for p, c in zip(prep_times, cook_times)]
        
        # Ingredient statistics
        total_ingredients_per_recipe = [len(r['ingredients']) for r in recipes]
        
        # Authenticity scores
        auth_scores = [r.get('authenticity_score', 0) for r in recipes]
        high_auth = len([s for s in auth_scores if s >= 0.9])
        
        stats = {
            'dataset_overview': {
                'total_recipes': len(recipes),
                'total_unique_ingredients': self.ingredient_data['total_ingredients'],
                'categories': len(categories),
                'trilingual_support': True,
                'date_created': self.recipe_data.get('created_date', datetime.now().isoformat())
            },
            'category_distribution': categories,
            'difficulty_distribution': difficulties,
            'time_statistics': {
                'avg_prep_time': np.mean(prep_times) if prep_times else 0,
                'avg_cook_time': np.mean(cook_times) if cook_times else 0,
                'avg_total_time': np.mean(total_times) if total_times else 0,
                'min_total_time': min(total_times) if total_times else 0,
                'max_total_time': max(total_times) if total_times else 0
            },
            'ingredient_statistics': {
                'avg_ingredients_per_recipe': np.mean(total_ingredients_per_recipe),
                'min_ingredients': min(total_ingredients_per_recipe),
                'max_ingredients': max(total_ingredients_per_recipe)
            },
            'quality_metrics': {
                'high_authenticity_recipes': high_auth,
                'high_authenticity_percentage': (high_auth / len(recipes) * 100) if recipes else 0,
                'recipes_with_cultural_notes': len([r for r in recipes if r.get('cultural_notes')]),
                'recipes_with_tips': len([r for r in recipes if r.get('tips')])
            }
        }
        
        return stats
    
    def generate_research_component_summary(self) -> Dict:
        """Summarize research components completed"""
        
        components = {
            'data_collection': {
                'status': 'Completed',
                'description': 'Collected and structured Sri Lankan recipe dataset',
                'achievements': [
                    f"{self.recipe_data['total_recipes']} authentic recipes collected",
                    "Trilingual support (English, Sinhala, Tamil)",
                    f"{self.ingredient_data['total_ingredients']} unique ingredients identified",
                    "Multiple data sources integrated (web, PDF, manual)"
                ]
            },
            'rag_implementation': {
                'status': 'Completed',
                'description': 'Implemented Retrieval-Augmented Generation system',
                'achievements': [
                    "Sentence-BERT embeddings for semantic search",
                    "FAISS vector database for efficient retrieval",
                    "Multilingual search support",
                    "Vector dimension: 384 (MiniLM model)"
                ]
            },
            'ingredient_matching': {
                'status': 'Completed',
                'description': 'Ingredient-based recipe recommendation system',
                'achievements': [
                    "Fuzzy matching algorithm",
                    "Grocery list generation",
                    "Trilingual ingredient mapping",
                    "Match percentage calculation"
                ]
            },
            'model_comparison': {
                'status': 'In Progress',
                'description': 'Comparison of different embedding models',
                'models_tested': [
                    {
                        'name': 'paraphrase-multilingual-MiniLM-L12-v2',
                        'pros': ['Multilingual', 'Fast', 'Good quality'],
                        'cons': ['Lower dimension than larger models'],
                        'dimension': 384
                    }
                ],
                'planned_comparisons': [
                    'Compare with mBERT',
                    'Compare with XLM-RoBERTa',
                    'Benchmark retrieval accuracy',
                    'Measure inference speed'
                ]
            }
        }
        
        if self.eval_metrics:
            components['rag_implementation']['achievements'].append(
                f"Search accuracy: {self.eval_metrics.get('overall_accuracy', 0):.1f}%"
            )
        
        return components
    
    def create_visualization_charts(self):
        """Create charts for presentation"""
        
        try:
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
        except:
            pass
        
        recipes = self.recipe_data['recipes']
        
        # Chart 1: Category Distribution
        categories = {}
        for recipe in recipes:
            cat = recipe['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        if categories:
            plt.figure(figsize=(10, 6))
            plt.bar(categories.keys(), categories.values(), color='skyblue')
            plt.title('Recipe Category Distribution', fontsize=14, fontweight='bold')
            plt.xlabel('Category')
            plt.ylabel('Number of Recipes')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(self.output_dir / 'category_distribution.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(f"OK Created chart: category_distribution.png")
        
        # Chart 2: Difficulty Distribution
        difficulties = {}
        for recipe in recipes:
            diff = recipe['difficulty']
            difficulties[diff] = difficulties.get(diff, 0) + 1
        
        if difficulties:
            plt.figure(figsize=(8, 6))
            colors = {'Easy': 'lightgreen', 'Medium': 'gold', 'Hard': 'salmon'}
            plt.pie(
                difficulties.values(),
                labels=difficulties.keys(),
                autopct='%1.1f%%',
                colors=[colors.get(k, 'gray') for k in difficulties.keys()],
                startangle=90
            )
            plt.title('Recipe Difficulty Distribution', fontsize=14, fontweight='bold')
            plt.savefig(self.output_dir / 'difficulty_distribution.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(f"OK Created chart: difficulty_distribution.png")
        
        # Chart 3: Cooking Time Distribution
        total_times = []
        for recipe in recipes:
            prep = recipe.get('prep_time_minutes', 0)
            cook = recipe.get('cook_time_minutes', 0)
            total_times.append(prep + cook)
        
        if total_times:
            plt.figure(figsize=(10, 6))
            plt.hist(total_times, bins=10, color='coral', edgecolor='black', alpha=0.7)
            plt.title('Cooking Time Distribution', fontsize=14, fontweight='bold')
            plt.xlabel('Total Time (minutes)')
            plt.ylabel('Number of Recipes')
            plt.axvline(np.mean(total_times), color='red', linestyle='--', label=f'Average: {np.mean(total_times):.0f} min')
            plt.legend()
            plt.tight_layout()
            plt.savefig(self.output_dir / 'cooking_time_distribution.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(f"OK Created chart: cooking_time_distribution.png")
    
    def generate_pp1_document(self, stats: Dict, components: Dict):
        """Generate PP1 presentation document"""
        
        doc_path = self.output_dir / 'PP1_RESEARCH_SUMMARY.md'
        
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write("# Progress Presentation 1 (PP1)\n")
            f.write("## AI-Powered Kitchen Echo System\n")
            f.write(f"### Date: {datetime.now().strftime('%B %d, %Y')}\n\n")
            
            f.write("---\n\n")
            
            # Project Overview
            f.write("## 1. Project Overview\n\n")
            f.write("**Objective:** Develop an AI-powered kitchen assistant that provides:\n")
            f.write("- Trilingual recipe recommendations (English, Sinhala, Tamil)\n")
            f.write("- Ingredient-based recipe matching\n")
            f.write("- Smart grocery list generation\n")
            f.write("- Cultural authenticity preservation\n\n")
            
            # Dataset Statistics
            f.write("## 2. Dataset Statistics\n\n")
            f.write(f"- **Total Recipes:** {stats['dataset_overview']['total_recipes']}\n")
            f.write(f"- **Unique Ingredients:** {stats['dataset_overview']['total_unique_ingredients']}\n")
            f.write(f"- **Categories:** {stats['dataset_overview']['categories']}\n")
            f.write(f"- **Language Support:** English, Sinhala, Tamil\n\n")
            
            f.write("### Category Breakdown:\n")
            for cat, count in stats['category_distribution'].items():
                f.write(f"- {cat}: {count} recipes\n")
            f.write("\n")
            
            f.write("### Quality Metrics:\n")
            f.write(f"- High Authenticity Recipes: {stats['quality_metrics']['high_authenticity_recipes']} ")
            f.write(f"({stats['quality_metrics']['high_authenticity_percentage']:.1f}%)\n")
            f.write(f"- Recipes with Cultural Notes: {stats['quality_metrics']['recipes_with_cultural_notes']}\n")
            f.write(f"- Recipes with Tips: {stats['quality_metrics']['recipes_with_tips']}\n\n")
            
            # Research Components
            f.write("## 3. Research Components Completed\n\n")
            
            for comp_name, comp_data in components.items():
                f.write(f"### {comp_name.replace('_', ' ').title()}\n")
                f.write(f"**Status:** {comp_data.get('status', 'Unknown')}\n\n")
                f.write(f"{comp_data.get('description', '')}\n\n")
                
                if 'achievements' in comp_data:
                    f.write("**Achievements:**\n")
                    for achievement in comp_data['achievements']:
                        f.write(f"- {achievement}\n")
                    f.write("\n")
            
            # Technical Implementation
            f.write("## 4. Technical Implementation\n\n")
            f.write("### Architecture:\n")
            f.write("```\n")
            f.write("User Query (any language)\n")
            f.write("    ↓\n")
            f.write("RAG System (Sentence-BERT Embeddings)\n")
            f.write("    ↓\n")
            f.write("FAISS Vector Search\n")
            f.write("    ↓\n")
            f.write("Recipe Retrieval & Ranking\n")
            f.write("    ↓\n")
            f.write("Ingredient Matching\n")
            f.write("    ↓\n")
            f.write("Grocery List Generation\n")
            f.write("    ↓\n")
            f.write("Trilingual Response\n")
            f.write("```\n\n")
            
            f.write("### Technologies Used:\n")
            f.write("- **Backend:** Python, Flask\n")
            f.write("- **Embeddings:** Sentence-BERT (Multilingual MiniLM)\n")
            f.write("- **Vector DB:** FAISS\n")
            f.write("- **NLP:** Transformers, fuzzy matching\n")
            f.write("- **Data:** JSON, CSV\n\n")
            
            # Results
            f.write("## 5. Preliminary Results\n\n")
            
            if self.eval_metrics:
                f.write(f"### RAG System Performance:\n")
                f.write(f"- Overall Search Accuracy: {self.eval_metrics.get('overall_accuracy', 0):.1f}%\n")
                f.write(f"- Test Queries: {self.eval_metrics.get('total_queries', 0)}\n\n")
                
                if 'language_accuracy' in self.eval_metrics:
                    f.write("### Per-Language Accuracy:\n")
                    for lang, acc in self.eval_metrics['language_accuracy'].items():
                        f.write(f"- {lang.title()}: {acc:.1f}%\n")
                    f.write("\n")
            
            f.write(f"### Time Performance:\n")
            f.write(f"- Average Recipe Prep Time: {stats['time_statistics']['avg_prep_time']:.1f} minutes\n")
            f.write(f"- Average Cook Time: {stats['time_statistics']['avg_cook_time']:.1f} minutes\n")
            f.write(f"- Total Time Range: {stats['time_statistics']['min_total_time']:.0f} - ")
            f.write(f"{stats['time_statistics']['max_total_time']:.0f} minutes\n\n")
            
            # Next Steps
            f.write("## 6. Next Steps (Before Final Presentation)\n\n")
            f.write("- [ ] Expand dataset to 200+ recipes\n")
            f.write("- [ ] Complete model comparison study\n")
            f.write("- [ ] Implement frontend interface\n")
            f.write("- [ ] Conduct user testing\n")
            f.write("- [ ] Optimize retrieval performance\n")
            f.write("- [ ] Add more ingredient translations\n\n")
            
            # Challenges
            f.write("## 7. Challenges & Solutions\n\n")
            f.write("### Challenge 1: Multilingual Support\n")
            f.write("**Solution:** Used multilingual sentence transformers that support Sinhala and Tamil\n\n")
            f.write("### Challenge 2: Data Collection\n")
            f.write("**Solution:** Combined web scraping, PDF extraction, and manual entry\n\n")
            f.write("### Challenge 3: Authenticity Preservation\n")
            f.write("**Solution:** Added cultural notes and authenticity scoring\n\n")
            
            # References
            f.write("## 8. References\n\n")
            f.write("- Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks\n")
            f.write("- FAISS: A Library for Efficient Similarity Search\n")
            f.write("- Transformers: State-of-the-art Natural Language Processing\n\n")
        
        print(f"OK Created PP1 document: {doc_path}")
    
    def generate_all(self):
        """Generate all PP1 materials"""
        
        print("\nSTATS Loading data...")
        self.load_data()
        
        print("\n📈 Generating statistics...")
        stats = self.generate_dataset_statistics()
        
        print("\n📋 Summarizing research components...")
        components = self.generate_research_component_summary()
        
        print("\nSTATS Creating visualizations...")
        try:
            self.create_visualization_charts()
        except Exception as e:
            print(f"WARNING Could not create charts: {e}")
            print("   Install matplotlib: pip install matplotlib")
        
        print("\n Generating PP1 document...")
        self.generate_pp1_document(stats, components)
        
        # Save JSON versions
        with open(self.output_dir / 'dataset_statistics.json', 'w') as f:
            json.dump(stats, f, indent=2)
        
        with open(self.output_dir / 'research_components.json', 'w') as f:
            json.dump(components, f, indent=2)
        
        print(f"\nOK ALL PP1 MATERIALS GENERATED!")
        print(f"📁 Location: {self.output_dir}")
        print("\nFiles created:")
        for file in self.output_dir.iterdir():
            print(f"  - {file.name}")


def main():
    prep = PP1Preparation()
    prep.generate_all()


if __name__ == "__main__":
    main()