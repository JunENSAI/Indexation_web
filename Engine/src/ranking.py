import math
from src.config import K1, B

def compute_stats_from_index(products_db):
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

def linear_score(bm25, review_mark, w1, w2):
    """Combinaison linéaire BM25 et Avis."""
    return (w1 * bm25) + (w2 * review_mark)