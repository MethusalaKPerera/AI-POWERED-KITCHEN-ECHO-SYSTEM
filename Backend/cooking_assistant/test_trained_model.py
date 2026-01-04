#!/usr/bin/env python3
"""
Trained Model Inference
Use your trained ML model to classify new recipes
"""

import json
import pickle
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
    LIBRARIES_AVAILABLE = True
except ImportError:
    LIBRARIES_AVAILABLE = False

def load_trained_model():
    """Load the trained model"""
    
    models_dir = Path('trained_models')
    
    # Load model
    with open(models_dir / 'recipe_classifier.pkl', 'rb') as f:
        model = pickle.load(f)
    
    # Load label encoder
    with open(models_dir / 'label_encoder.pkl', 'rb') as f:
        label_encoder = pickle.load(f)
    
    # Load info
    with open(models_dir / 'model_info.json', 'r') as f:
        info = json.load(f)
    
    # Load embedding model
    embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    return model, label_encoder, embedding_model, info

def predict_category(text, model, label_encoder, embedding_model):
    """Predict category for a recipe"""
    
    # Generate embedding
    embedding = embedding_model.encode([text])
    
    # Predict
    prediction = model.predict(embedding)[0]
    probabilities = model.predict_proba(embedding)[0]
    
    # Decode
    category = label_encoder.inverse_transform([prediction])[0]
    confidence = probabilities[prediction] * 100
    
    # Get top 3 predictions
    top3_indices = probabilities.argsort()[-3:][::-1]
    top3 = [
        {
            "category": label_encoder.inverse_transform([idx])[0],
            "confidence": probabilities[idx] * 100
        }
        for idx in top3_indices
    ]
    
    return category, confidence, top3

def demo_inference():
    """Demo the trained model"""
    
    print("\n" + "="*70)
    print("TRAINED MODEL INFERENCE DEMO")
    print("="*70 + "\n")
    
    if not LIBRARIES_AVAILABLE:
        print("❌ Libraries not available!")
        return
    
    # Load model
    print("Loading trained model...")
    model, label_encoder, embedding_model, info = load_trained_model()
    
    print(f"✅ Loaded: {info['model_type']}")
    print(f"✅ Accuracy: {info['accuracy']*100:.2f}%")
    print(f"✅ Classes: {', '.join(info['classes'])}\n")
    
    # Test examples
    test_cases = [
        {
            "name": "Spicy Chicken with Coconut Milk",
            "description": "A rich curry made with chicken, coconut milk, and Sri Lankan spices",
            "ingredients": ["chicken", "coconut milk", "curry powder", "onions"]
        },
        {
            "name": "Sweet Coconut Balls",
            "description": "Traditional sweet made with coconut and jaggery",
            "ingredients": ["coconut", "jaggery", "rice flour"]
        },
        {
            "name": "Pol Sambol",
            "description": "Spicy coconut relish with chili and lime",
            "ingredients": ["coconut", "chili", "onion", "lime"]
        }
    ]
    
    print("Testing model on sample recipes:\n")
    
    for i, test in enumerate(test_cases, 1):
        text = f"{test['name']}. {test['description']}. Ingredients: {', '.join(test['ingredients'])}."
        
        category, confidence, top3 = predict_category(text, model, label_encoder, embedding_model)
        
        print(f"{i}. {test['name']}")
        print(f"   ✅ Predicted: {category} ({confidence:.1f}% confidence)")
        print(f"   📊 Top 3 predictions:")
        for rank, pred in enumerate(top3, 1):
            print(f"      {rank}. {pred['category']}: {pred['confidence']:.1f}%")
        print()
    
    print("="*70)
    print("✅ Your trained model is working!")
    print("="*70)

if __name__ == "__main__":
    demo_inference()
