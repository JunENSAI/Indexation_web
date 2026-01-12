import json

def save_to_json(results, filename='products.json'):
    """Sauvegarde les résultats dans un fichier JSON (format JSONL)"""
    with open(filename, 'w', encoding='utf-8') as f:
        for result in results:
            json.dump(result, f, ensure_ascii=False)
            f.write('\n')
    print(f"Résultats sauvegardés dans {filename}")