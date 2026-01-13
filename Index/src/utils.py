import json
import string
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

stop_words = set(stopwords.words('english'))

def load_jsonl(filepath):
    """Lecture du fichier JSONL ligne par ligne."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f]

def save_json(data, filepath):
    """Sauvegarde des dictionnaires dans des fichiers JSON."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def extract_product_info(url):
    """
    Extraire ID et variante de l'URL.
    """
    product_id = "N/A"
    variant = None

    match_id = re.search(r'product/(\d+)', url)
    if match_id:
        product_id = match_id.group(1)
        
    match_var = re.search(r'variant=([^&]+)', url)
    if match_var:
        variant = match_var.group(1)
        
    return {"id": product_id, "variant": variant}

def tokenize(text):
    """
    Tokenization par espace, suppression ponctuation et stopwords.
    """
    if not text:
        return []
    
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text)
    return [t for t in tokens if t not in stop_words]