import json
import os

def load_json(filepath):
    """Charge un fichier JSON."""
    if not os.path.exists(filepath):
        print(f"Fichier introuvable : {filepath}")
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_products_jsonl(filepath):
    """
    Charge le fichier products.jsonl et crée un dictionnaire accessible par URL.
    Sert à l'affichage final et au calcul de la longueur des documents.
    """
    db = {}
    if not os.path.exists(filepath):
        print(f"Fichier produits introuvable : {filepath}")
        return db
        
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                doc = json.loads(line)
                url = doc.get("url")
                if url:
                    db[url] = doc
            except json.JSONDecodeError:
                continue
    return db