WEIGHTS = {
    "bm25": 0.6,
    "title": 0.4,
    "reviews": 0.3,
    "position": 0.1,  
}

K1 = 1.2
B = 0.75

FILES = {
    "products": "../Engine/input/rearranged_products.jsonl",
    "title_index": "../Engine/input/title_index.json",
    "origin_index": "../Engine/input/origin_index.json",
    "reviews_index": "../Engine/input/reviews_index.json",
    "product_synonyms": "../Engine/input/products_synonyms.json",
    "origin_synonyms": "../Engine/input/origin_synonyms.json"
}