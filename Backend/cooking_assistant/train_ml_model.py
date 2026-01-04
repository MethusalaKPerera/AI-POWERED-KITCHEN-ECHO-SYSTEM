#!/usr/bin/env python3
"""
Recipe Classification Model Training
Train your OWN ML model on your recipe dataset
Perfect for research - real model training with evaluation
"""

import json
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pickle

# Check for required libraries
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC
    import warnings
    warnings.filterwarnings('ignore')
    LIBRARIES_AVAILABLE = True
except ImportError:
    LIBRARIES_AVAILABLE = False
    print("❌ Required libraries not installed!")
    print("Install: pip install scikit-learn sentence-transformers --break-system-packages")

def prepare_training_data():
    """
    Prepare training data from recipes
    Task: Classify recipes into categories
    """
    
    print("\n" + "="*80)
    print("STEP 1: PREPARING TRAINING DATA")
    print("="*80 + "\n")
    
    # Load recipes
    with open('rag/data/recipes/recipe_database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        recipes = data['recipes']
    
    print(f"📚 Loaded {len(recipes)} recipes")
    
    # Prepare features and labels
    texts = []
    labels = []
    recipe_ids = []
    
    for recipe in recipes:
        # Combine text for better features
        text = f"{recipe['name']}. {recipe.get('description', '')}. "
        text += f"Ingredients: {', '.join(recipe.get('ingredients', [])[:10])}."
        
        texts.append(text)
        labels.append(recipe['category'])
        recipe_ids.append(recipe['id'])
    
    # Analyze label distribution
    label_counts = {}
    for label in labels:
        label_counts[label] = label_counts.get(label, 0) + 1
    
    print(f"\n📊 Dataset Distribution:")
    for label, count in sorted(label_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {label}: {count} recipes ({count/len(labels)*100:.1f}%)")
    
    # Encode labels
    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(labels)
    
    print(f"\n✅ Prepared {len(texts)} training samples")
    print(f"✅ Number of classes: {len(label_encoder.classes_)}")
    print(f"✅ Classes: {', '.join(label_encoder.classes_)}")
    
    return texts, encoded_labels, label_encoder, recipe_ids

def generate_embeddings(texts):
    """
    Generate embeddings using Sentence-BERT
    """
    
    print("\n" + "="*80)
    print("STEP 2: GENERATING EMBEDDINGS")
    print("="*80 + "\n")
    
    print("Loading Sentence-BERT model...")
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    print(f"Generating embeddings for {len(texts)} recipes...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    
    print(f"\n✅ Generated embeddings: {embeddings.shape}")
    
    return embeddings

def train_models(X_train, X_test, y_train, y_test, label_encoder):
    """
    Train multiple ML models and compare
    """
    
    print("\n" + "="*80)
    print("STEP 3: TRAINING ML MODELS")
    print("="*80 + "\n")
    
    models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1),
        "SVM": SVC(kernel='rbf', random_state=42, probability=True)
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\n{'='*60}")
        print(f"Training: {name}")
        print('='*60)
        
        # Train
        print("Training...")
        model.fit(X_train, y_train)
        
        # Predict
        print("Evaluating...")
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        # Store results
        results[name] = {
            "model": model,
            "accuracy": accuracy,
            "predictions": y_pred
        }
        
        print(f"\n✅ {name} Training Complete!")
        print(f"   Accuracy: {accuracy*100:.2f}%")
        
        # Show classification report
        print(f"\n📊 Classification Report:")
        print(classification_report(y_test, y_pred, target_names=label_encoder.classes_, zero_division=0))
    
    return results

def save_best_model(results, label_encoder, embeddings):
    """
    Save the best performing model
    """
    
    print("\n" + "="*80)
    print("STEP 4: SAVING BEST MODEL")
    print("="*80 + "\n")
    
    # Find best model
    best_name = max(results.keys(), key=lambda k: results[k]['accuracy'])
    best_model = results[best_name]['model']
    best_accuracy = results[best_name]['accuracy']
    
    print(f"🏆 Best Model: {best_name}")
    print(f"🎯 Accuracy: {best_accuracy*100:.2f}%")
    
    # Create models directory
    models_dir = Path('trained_models')
    models_dir.mkdir(exist_ok=True)
    
    # Save model
    model_file = models_dir / 'recipe_classifier.pkl'
    with open(model_file, 'wb') as f:
        pickle.dump(best_model, f)
    
    # Save label encoder
    encoder_file = models_dir / 'label_encoder.pkl'
    with open(encoder_file, 'wb') as f:
        pickle.dump(label_encoder, f)
    
    # Save training info
    info = {
        "model_type": best_name,
        "accuracy": float(best_accuracy),
        "num_classes": len(label_encoder.classes_),
        "classes": label_encoder.classes_.tolist(),
        "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2",
        "embedding_dim": embeddings.shape[1],
        "training_samples": len(embeddings),
        "date": "2026-01-04"
    }
    
    info_file = models_dir / 'model_info.json'
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2)
    
    print(f"\n💾 Saved model to: {model_file}")
    print(f"💾 Saved encoder to: {encoder_file}")
    print(f"💾 Saved info to: {info_file}")
    
    return best_name, best_accuracy

def main():
    """
    Complete ML training pipeline
    """
    
    print("\n" + "="*80)
    print(" " * 20 + "ML MODEL TRAINING PIPELINE")
    print(" " * 15 + "Recipe Category Classification")
    print("="*80)
    
    if not LIBRARIES_AVAILABLE:
        print("\n❌ Please install required libraries first!")
        print("Run: pip install scikit-learn sentence-transformers --break-system-packages")
        return
    
    # Step 1: Prepare data
    texts, labels, label_encoder, recipe_ids = prepare_training_data()
    
    # Step 2: Generate embeddings
    embeddings = generate_embeddings(texts)
    
    # Step 3: Split data (80% train, 20% test)
    print("\n" + "="*80)
    print("SPLITTING DATA (80% train, 20% test)")
    print("="*80 + "\n")
    
    X_train, X_test, y_train, y_test = train_test_split(
        embeddings, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Step 4: Train models
    results = train_models(X_train, X_test, y_train, y_test, label_encoder)
    
    # Step 5: Save best model
    best_name, best_accuracy = save_best_model(results, label_encoder, embeddings)
    
    # Final summary
    print("\n" + "="*80)
    print("TRAINING COMPLETE!")
    print("="*80)
    
    print(f"\n🎉 Successfully trained ML model!")
    print(f"\n📊 Final Results:")
    print(f"   - Best Model: {best_name}")
    print(f"   - Accuracy: {best_accuracy*100:.2f}%")
    print(f"   - Training Samples: {len(X_train)}")
    print(f"   - Test Samples: {len(X_test)}")
    print(f"   - Number of Classes: {len(label_encoder.classes_)}")
    
    print(f"\n✅ Model saved in: trained_models/")
    print(f"\n🔬 FOR RESEARCH PAPER:")
    print(f"   - Dataset: 190 recipes")
    print(f"   - Task: Multi-class classification ({len(label_encoder.classes_)} categories)")
    print(f"   - Features: Sentence-BERT embeddings (384-dim)")
    print(f"   - Model: {best_name}")
    print(f"   - Train/Test Split: 80/20")
    print(f"   - Accuracy: {best_accuracy*100:.2f}%")
    
    print("\n" + "="*80)
    print("NEXT: Create inference script to use your trained model!")
    print("="*80)

if __name__ == "__main__":
    main()
