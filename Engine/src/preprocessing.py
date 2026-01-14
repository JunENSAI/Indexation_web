import re
import os
import json
import nltk
from nltk.corpus import stopwords

def init_nltk():
    """Télécharge les ressources NLTK si nécessaire."""
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)

def get_stopwords_set():
    """Récupère le set de stopwords anglais."""
    return set(stopwords.words("english"))

def tokenize(text):
    """
    Tokenization simple: minuscule + alphanumérique.
    Identique au TP précédent comme demandé.
    """
    if not text:
        return []
    return re.findall(r'\b\w+\b', text.lower())

def flatten_synonyms(data):
    flat_map = {}
    for key, variants in data.items():
        main_term = key.lower()
        group = set([main_term])
        for v in variants:
            group.add(v.lower())

        for word in group:
            if word not in flat_map:
                flat_map[word] = set()
            flat_map[word].update(group)
    return flat_map

def load_and_merge_synonyms(filepath_list):
    """
    Charge plusieurs fichiers JSON de synonymes et les fusionne en un seul mapping.
    """
    merged_map = {}
    
    for filepath in filepath_list:
        if not os.path.exists(filepath):
            print(f"Fichier synonymes ignoré (introuvable) : {filepath}")
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                current_flat = flatten_synonyms(data)

                for word, synonyms_set in current_flat.items():
                    if word not in merged_map:
                        merged_map[word] = set()
                    merged_map[word].update(synonyms_set)
                    
            except json.JSONDecodeError:
                print(f"Erreur de syntaxe JSON dans : {filepath}")
                
    return merged_map

def expand_query(query_tokens, synonyms_db):
    """
    Augmentation de la requête par synonymes.
    Vérifie si un token a des synonymes et les ajoute.
    """
    expanded = set(query_tokens)
    for token in query_tokens:
        if token in synonyms_db:
            expanded.update(synonyms_db[token])
    return list(expanded)