import json
from src import config, preprocessing, utils, ranking

def main():
    preprocessing.init_nltk()
    stop_words = preprocessing.get_stopwords_set()
    
    title_index = utils.load_json(config.FILES['title_index'])
    origin_index = utils.load_json(config.FILES['origin_index'])
    reviews_index = utils.load_json(config.FILES['reviews_index'])
    products_db = utils.load_products_jsonl(config.FILES['products'])
    url_to_origin = {}
    for country, data in origin_index.items():
        if isinstance(data, list):
            urls = data
        elif isinstance(data, dict):
            urls = data.keys()
        else:
            urls = []
            
        for u in urls:
            url_to_origin[u] = country.capitalize()

    print("Chargement et fusion des dictionnaires de synonymes...")
    synonyms_files = [
        config.FILES['origin_synonyms'], 
        config.FILES['product_synonyms']
    ]
    
    if products_db:
        doc_lengths, avg_dl, total_docs = ranking.compute_stats_from_index(products_db)
    else:
        from src.ranking import compute_stats_from_index
        doc_lengths, avg_dl, total_docs = compute_stats_from_index(title_index)
    
    synonyms_map = preprocessing.load_and_merge_synonyms(synonyms_files)

    while True:
        print("-" * 50)
        query_raw = input("\n Entrez votre recherche (ex: 'blue usa') : ").strip()
        
        if query_raw.lower() in ['exit', 'quit']:
            print("À une prochaine !")
            break
        
        if not query_raw:
            continue

        original_tokens = preprocessing.tokenize(query_raw)
        expanded_tokens_for_ranking = preprocessing.expand_query(original_tokens, synonyms_map)

        candidate_docs = set()
        is_first_concept = True

        for token in original_tokens:
            if token in stop_words:
                continue

            variants = {token}
            if token in synonyms_map:
                variants.update(synonyms_map[token])
            
            docs_for_this_concept = set()
            for v in variants:
                t_matches = title_index.get(v, {})
                if isinstance(t_matches, dict):
                    docs_for_this_concept.update(t_matches.keys())
                elif isinstance(t_matches, list):
                    docs_for_this_concept.update(t_matches)
                
                o_matches = origin_index.get(v, [])
                if isinstance(o_matches, dict):
                    docs_for_this_concept.update(o_matches.keys())
                elif isinstance(o_matches, list):
                    docs_for_this_concept.update(o_matches)
                    
            if is_first_concept:
                candidate_docs = docs_for_this_concept
                is_first_concept = False
            else:
                candidate_docs.intersection_update(docs_for_this_concept)

            if not candidate_docs:
                break

        if not candidate_docs:
            print("Aucun résultat trouvé.")
            continue

        print(f"   Concepts traités : {original_tokens}")
        print(f"   Documents candidats : {len(candidate_docs)}")

        results = []
        for url in candidate_docs:
            s_bm25 = ranking.bm25_score(expanded_tokens_for_ranking, url, title_index, doc_lengths, avg_dl, total_docs)
            s_reviews = reviews_index.get(url, {}).get('mean_mark', 0)
            
            final_score = ranking.linear_score(s_bm25, s_reviews, config.WEIGHT_BM25, config.WEIGHT_REVIEWS)
            
            product_info = products_db.get(url, {})
            
            origin_display = url_to_origin.get(url, "N/A")
            
            results.append({
                "title": product_info.get("title", "Titre Inconnu"),
                "url": url,
                "origin": origin_display,
                "score": round(final_score, 4)
            })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n {len(results)} Résultats trouvés :\n")
        for i, res in enumerate(results[:5]):
            print(f"{i+1}. {res['title']} (Score: {res['score']})")
            print(f"   Origine: {res.get('origin', '?')} | URL: {res['url']}")
            print("")

if __name__ == "__main__":
    main()