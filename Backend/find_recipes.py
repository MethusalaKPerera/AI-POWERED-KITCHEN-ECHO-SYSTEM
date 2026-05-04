import os
import json

print("Searching for recipe databases...\n")

for root, dirs, files in os.walk('.'):
    # Skip node_modules and hidden folders
    dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__']]
    
    for f in files:
        if f.endswith('.json'):
            fp = os.path.join(root, f)
            try:
                with open(fp, 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                
                count = 0
                if isinstance(data, list):
                    count = len(data)
                elif isinstance(data, dict):
                    count = len(data.get('recipes', []))
                
                if count > 10:
                    print(f"{count} recipes --> {fp}")
                    
            except Exception:
                pass

print("\nDone.")