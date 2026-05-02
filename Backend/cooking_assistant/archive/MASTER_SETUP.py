#!/usr/bin/env python3
"""
MASTER SETUP SCRIPT FOR PP1 PREPARATION
AI-Powered Kitchen Echo System

Runs all components in correct order:
1. Setup project structure
2. Collect sample recipes
3. Build RAG system
4. Create ingredient matcher
5. Generate PP1 materials

Run this script to prepare everything for PP1!
"""

import subprocess
import sys
from pathlib import Path
import time


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"🍛 {text}")
    print("="*70 + "\n")


def print_step(step_num, text):
    """Print step"""
    print(f"\n{'='*70}")
    print(f"STEP {step_num}: {text}")
    print(f"{'='*70}\n")


def run_script(script_path, description):
    """Run a Python script and show output"""
    print(f"▶️  Running: {description}")
    print(f"   Script: {script_path}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS\n")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}\n")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏱️ {description} - TIMEOUT (may need more time)\n")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}\n")
        return False


def install_dependencies():
    """Install required Python packages"""
    print_step(1, "INSTALLING DEPENDENCIES")
    
    packages = [
        'sentence-transformers',
        'faiss-cpu',
        'matplotlib',
        'numpy',
        'requests',
        'beautifulsoup4',
        'lxml'
    ]
    
    print("📦 Installing Python packages...")
    for package in packages:
        print(f"   Installing {package}...")
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', package, '--break-system-packages', '--quiet'],
                timeout=120
            )
            print(f"   ✅ {package} installed")
        except Exception as e:
            print(f"   ⚠️ {package} installation issue (may already be installed)")
    
    print("\n✅ Dependencies installation complete!")


def setup_project_structure():
    """Create project directory structure"""
    print_step(2, "SETTING UP PROJECT STRUCTURE")
    
    base_dir = Path('Backend/cooking_assistant')
    
    directories = [
        base_dir / 'rag' / 'data' / 'recipes',
        base_dir / 'rag' / 'data' / 'embeddings',
        base_dir / 'rag' / 'data' / 'processed',
        base_dir / 'data' / 'sri_lankan_recipes',
        base_dir / 'data' / 'extracted',
        base_dir / 'data' / 'raw_pdfs',
        base_dir / 'pp1_materials'
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")
    
    print("\n✅ Project structure ready!")


def main():
    """Main execution flow"""
    
    print_header("PP1 PREPARATION - COMPLETE SETUP")
    print("This script will prepare EVERYTHING for your PP1 presentation!")
    print("\nEstimated time: 10-15 minutes")
    
    input("\nPress Enter to start...")
    
    start_time = time.time()
    
    # Step 1: Install dependencies
    install_dependencies()
    
    # Step 2: Setup structure
    setup_project_structure()
    
    # Step 3: Collect recipes
    print_step(3, "COLLECTING SAMPLE RECIPES")
    success = run_script('integrated_recipe_collector.py', 'Recipe Collection')
    
    if not success:
        print("⚠️ Recipe collection had issues, but continuing...")
    
    # Step 4: Build RAG system
    print_step(4, "BUILDING RAG SYSTEM")
    success = run_script('recipe_rag_system.py', 'RAG System Build')
    
    if not success:
        print("⚠️ RAG system build had issues, but continuing...")
    
    # Step 5: Generate PP1 materials
    print_step(5, "GENERATING PP1 MATERIALS")
    success = run_script('pp1_preparation.py', 'PP1 Materials Generation')
    
    if not success:
        print("⚠️ PP1 generation had issues, check output above")
    
    # Complete
    elapsed_time = time.time() - start_time
    
    print_header("SETUP COMPLETE!")
    
    print(f"⏱️ Total time: {elapsed_time/60:.1f} minutes\n")
    
    print("📁 Your files are ready:")
    print("   Backend/cooking_assistant/rag/data/recipes/ - Recipe database")
    print("   Backend/cooking_assistant/rag/data/embeddings/ - RAG embeddings")
    print("   Backend/cooking_assistant/pp1_materials/ - PP1 presentation materials")
    
    print("\n📊 PP1 Materials:")
    pp1_dir = Path('Backend/cooking_assistant/pp1_materials')
    if pp1_dir.exists():
        for file in pp1_dir.iterdir():
            print(f"   ✅ {file.name}")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Review Backend/cooking_assistant/pp1_materials/PP1_RESEARCH_SUMMARY.md")
    print("2. Check the visualization charts")
    print("3. Test the ingredient matcher: python ingredient_matcher.py")
    print("4. Prepare your presentation slides")
    
    print("\n" + "="*70)
    print("Good luck with your PP1! 🚀")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        print("\nCheck the error messages above for details.")