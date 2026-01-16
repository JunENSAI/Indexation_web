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

    synonyms_files = [
        config.FILES['origin_synonyms'], 
        config.FILES['product_synonyms']
    ]
    
    doc_lengths, avg_dl, total_docs = ranking.compute_stats(products_db)
    
    synonyms_map = preprocessing.load_and_merge_synonyms(synonyms_files)

    print("Moteur prêt. Tapez 'exit' pour quitter.")

    while True:
        print("-" * 100)
        query_raw = input("\nRecherche : ").strip()
        if query_raw.lower() in ['exit', 'quit']:
            break

        original_tokens = preprocessing.tokenize(query_raw)
        expanded_tokens = preprocessing.expand_query(original_tokens, synonyms_map)

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

        for token in expanded_tokens:
            if token in title_index:
                if isinstance(title_index[token], dict):
                    candidate_docs.update(title_index[token].keys())
                else:
                    candidate_docs.update(title_index[token])
                    
        scored_results = []
        
        for url in candidate_docs:
            doc_data = products_db.get(url, {})
            title = doc_data.get("title", "")
            description = doc_data.get("description", "")

            s_bm25 = ranking.bm25_score(expanded_tokens, url, title_index, doc_lengths, avg_dl, total_docs)
            s_reviews = reviews_index.get(url, {}).get('mean_mark', 0)
            s_title = ranking.title_match_score(original_tokens, title)
            s_pos = ranking.position_score(original_tokens, url, title_index)
            
            components = {
                "bm25": round(s_bm25,3),
                "reviews": round(s_reviews,3),
                "title": s_title,
                "position": round(s_pos,3)
            }

            final_score = ranking.linear_score(components, config.WEIGHTS)
            
            scored_results.append({
                "title": title,
                "url": url,
                "description": description,
                "score": round(final_score,3),
                "details": components
            })

        scored_results.sort(key=lambda x: x['score'], reverse=True)
        top_results = scored_results[:10]

        output_response = {
            "metadata": {
                "query": query_raw,
                "nombre_total_doc": total_docs,
                "doc_filtre": len(candidate_docs)
            },
            "results": top_results
        }
        print(json.dumps(output_response, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()