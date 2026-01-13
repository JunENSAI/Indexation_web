from src.utils import tokenize

def index_features(documents, feature_key):
    """
    Index inversé par feature (Marque, Origine).
    Structure: { valeur_feature: [urls] }
    """
    index = {}
    
    for doc in documents:
        url = doc['url']
        features = doc.get('product_features', {})
        
        value = features.get(feature_key)
        
        if value:
            key = value.lower()
            
            if key not in index:
                index[key] = []
            
            if url not in index[key]:
                index[key].append(url)
                
    return index

def index_reviews(documents):
    """
    Index des reviews (NON inversé).
    Structure: { url: { total_reviews, mean_mark, last_rating } }
    """
    index = {}
    
    for doc in documents:
        url = doc['url']
        reviews = doc.get('product_reviews', [])
        
        total = len(reviews)
        mean_mark = 0
        last_rating = 0
        
        if total > 0:
            total_stars = sum(r['rating'] for r in reviews)
            mean_mark = round(total_stars / total, 1)

            sorted_reviews = sorted(reviews, key=lambda x: x['date'])
            last_rating = sorted_reviews[-1]['rating']
            
        index[url] = {
            "total_reviews": total,
            "mean_mark": mean_mark,
            "last_rating": last_rating
        }
        
    return index

def positional_index(documents, field):
    """
    Index inversé de position pour Titre et Description.
    Structure: { token: { url: [positions] } }
    """
    index = {}
    
    for doc in documents:
        url = doc['url']
        content = doc.get(field, "")
        tokens = tokenize(content)
        
        for pos, token in enumerate(tokens):
            if token not in index:
                index[token] = {}
            
            if url not in index[token]:
                index[token][url] = []
            
            index[token][url].append(pos)
            
    return index
