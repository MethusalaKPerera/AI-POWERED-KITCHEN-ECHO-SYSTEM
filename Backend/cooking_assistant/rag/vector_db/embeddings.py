import os
import json
import numpy as np
from typing import Dict, List, Any

class EmbeddingManager:
    """Manages recipe embeddings and vector operations"""
    
    def __init__(self, embeddings_dir: str):
        self.embeddings_dir = embeddings_dir
        self.embeddings = {}
        self.config = {}
        self._ensure_dir()
    
    def _ensure_dir(self):
        os.makedirs(self.embeddings_dir, exist_ok=True)
    
    def save_config(self, config: Dict[str, Any]):
        config_path = os.path.join(self.embeddings_dir, 'config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        self.config = config
        print(f"✓ Config saved to {config_path}")
    
    def load_config(self) -> Dict[str, Any]:
        config_path = os.path.join(self.embeddings_dir, 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
                print(f"✓ Config loaded from {config_path}")
        return self.config
    
    def store_embeddings(self, embeddings: Dict[str, List[float]]):
        embeddings_path = os.path.join(self.embeddings_dir, 'recipe_embeddings.json')
        with open(embeddings_path, 'w') as f:
            json.dump(embeddings, f)
        self.embeddings = embeddings
        print(f"✓ Stored embeddings for {len(embeddings)} recipes")
    
    def load_embeddings(self) -> Dict[str, List[float]]:
        embeddings_path = os.path.join(self.embeddings_dir, 'recipe_embeddings.json')
        if os.path.exists(embeddings_path):
            with open(embeddings_path, 'r') as f:
                self.embeddings = json.load(f)
                print(f"✓ Loaded embeddings for {len(self.embeddings)} recipes")
        return self.embeddings
    
    def save_evaluation_metrics(self, metrics: Dict[str, Any]):
        metrics_path = os.path.join(self.embeddings_dir, 'evaluation_metrics.json')
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"✓ Metrics saved to {metrics_path}")