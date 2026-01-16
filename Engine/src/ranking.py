import math
from src.config import K1, B

def compute_stats(products_db):
    """
    Reconstruit les longueurs de documents à partir de l'index inversé.
    Nécessaire car nous n'avons pas le fichier products.jsonl.
    """
    doc_lengths = {}
    total_len = 0
    
    for url, data in products_db.items():
        content = (data.get("title", "") + " " + data.get("description", ""))
        length = len(content.split())
        doc_lengths[url] = length
        total_len += length
    
    total_docs = len(products_db)
    avg_dl = total_len / total_docs if total_docs > 0 else 1
    return doc_lengths, avg_dl, total_docs

def bm25_score(query_tokens, doc_url, index, doc_lengths, avg_dl, total_docs):
    """Calcule le score BM25."""
    score = 0.0
    doc_len = doc_lengths.get(doc_url, avg_dl)
    
    for token in query_tokens:
        if token not in index:
            continue
        
        postings = index[token]
        if doc_url not in postings:
            continue
            
        tf = len(postings[doc_url])
        
        n_q = len(postings)

        idf = math.log((total_docs - n_q + 0.5) / (n_q + 0.5) + 1)
        numerator = tf * (K1 + 1)
        denominator = tf + K1 * (1 - B + B * (doc_len / avg_dl))
        
        score += idf * (numerator / denominator)
        
    return score

def position_score(query_tokens, doc_url, index):
    """
    Utilise l'information de position si disponible
    Plus le mot apparaît tôt (position petite), meilleur est le score.
    """
    score = 0.0
    for token in query_tokens:
        if token in index and doc_url in index[token]:
            positions = index[token][doc_url]
            if not positions: continue

            first_pos = min(positions)
            
            score += 1.0 / (1.0 + math.log(first_pos + 1))
            
    return score

def title_match_score(query_tokens, doc_title):
    """
    Score binaire ou proportionnel pour la présence dans le titre.
    """
    if not doc_title: return 0.0
    
    matches = 0
    normalized_title = doc_title.lower()
    for token in query_tokens:
        if token in normalized_title:
            matches += 1
            
    return matches / len(query_tokens) if query_tokens else 0.0

def linear_score(components, weights):
    """
    Fonction de scoring linéaire générique.
    
    Args:
        components (dict): Dictionnaire des scores bruts 
                           ex: {'bm25': 2.5, 'reviews': 4.5, 'title': 1.0}
        weights (dict): Dictionnaire des poids correspondants
                        ex: {'bm25': 0.6, 'reviews': 0.2, 'title': 0.5}
    """
    final_score = 0.0
    for key in components:
        w = weights.get(key, 0.0)
        s = components[key]
        final_score += w * s
        
    return final_score