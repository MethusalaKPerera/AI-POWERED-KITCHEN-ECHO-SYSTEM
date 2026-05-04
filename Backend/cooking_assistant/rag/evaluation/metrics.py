from typing import List, Dict, Any
import json
import os

class RAGEvaluator:
    """Evaluates RAG system performance"""

    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or '.'
        self.metrics = {
            'precision': [],
            'recall': [],
            'f1_score': [],
            'queries': [],
        }

    def _get_id(self, item) -> str:
        """Safely extract ID from a recipe dict or string"""
        if isinstance(item, dict):
            return str(item.get('id', ''))
        return str(item)

    def calculate_precision(self, retrieved: List[Dict], relevant: List[Dict]) -> float:
        if not retrieved:
            return 0.0

        relevant_ids  = {self._get_id(r) for r in relevant}
        retrieved_ids = {self._get_id(r) for r in retrieved}

        intersection = len(relevant_ids & retrieved_ids)
        return intersection / len(retrieved_ids) if retrieved_ids else 0.0

    def calculate_recall(self, retrieved: List[Dict], relevant: List[Dict]) -> float:
        if not relevant:
            return 0.0

        relevant_ids  = {self._get_id(r) for r in relevant}
        retrieved_ids = {self._get_id(r) for r in retrieved}

        intersection = len(relevant_ids & retrieved_ids)
        return intersection / len(relevant_ids) if relevant_ids else 0.0

    def calculate_f1(self, precision: float, recall: float) -> float:
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)

    def evaluate_query(self, query: str, retrieved: List[Dict], relevant: List[Dict]) -> Dict[str, Any]:
        precision = self.calculate_precision(retrieved, relevant)
        recall    = self.calculate_recall(retrieved, relevant)
        f1        = self.calculate_f1(precision, recall)

        result = {
            'query':     query,
            'precision': round(precision, 4),
            'recall':    round(recall, 4),
            'f1_score':  round(f1, 4),
        }

        self.metrics['precision'].append(precision)
        self.metrics['recall'].append(recall)
        self.metrics['f1_score'].append(f1)
        self.metrics['queries'].append(query)

        return result

    def get_summary(self) -> Dict[str, float]:
        def safe_avg(values):
            return round(sum(values) / len(values), 4) if values else 0.0

        return {
            'avg_precision': safe_avg(self.metrics['precision']),
            'avg_recall':    safe_avg(self.metrics['recall']),
            'avg_f1':        safe_avg(self.metrics['f1_score']),
            'total_queries': len(self.metrics['queries']),
        }

    def save_metrics(self, filename: str = 'rag_metrics.json'):
        output_path = os.path.join(self.output_dir, filename)
        data = {
            'metrics': self.metrics,
            'summary': self.get_summary(),
        }
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Metrics saved to {output_path}")