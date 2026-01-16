from src import config, preprocessing, utils, ranking

title_index = utils.load_json(config.FILES['title_index'])
origin_index = utils.load_json(config.FILES['origin_index'])
reviews_index = utils.load_json(config.FILES['reviews_index'])
products_db = utils.load_products_jsonl(config.FILES['products'])

synonyms_files = [
    config.FILES['origin_synonyms'], 
    config.FILES['product_synonyms']
    ]
    
doc_lengths, avg_dl, total_docs = ranking.compute_stats(products_db)
synonyms_map = preprocessing.load_and_merge_synonyms(synonyms_files)


def test_config_parameters(products_db, title_index, origin_index, reviews_index, 
                       doc_lengths, avg_dl, total_docs, synonyms_map):
    """
    Exécute un jeu de requêtes prédéfini pour valider le comportement du moteur.
    """
    test_queries = [
        "basket bleu",
        "Beanie small",
        "teal potion",
        "womens sandals",
        "running shoes usa" 
    ]

    for query in test_queries:
        print(f"\n -- test requete : '{query}'")

        original_tokens = preprocessing.tokenize(query)
        expanded_tokens = preprocessing.expand_query(original_tokens, synonyms_map)

        candidate_docs = None
        stop_words = preprocessing.get_stopwords_set()
        
        for word in original_tokens:
            if word in stop_words: continue
            concept_variants = {word}
            if word in synonyms_map: concept_variants.update(synonyms_map[word])
            
            docs_with_concept = set()
            for variant in concept_variants:
                if variant in title_index:
                    matches = title_index[variant]
                    docs_with_concept.update(matches.keys() if isinstance(matches, dict) else matches)
                if variant in origin_index:
                    matches = origin_index[variant]
                    docs_with_concept.update(matches.keys() if isinstance(matches, dict) else matches)

            if candidate_docs is None:
                candidate_docs = docs_with_concept
            else:
                candidate_docs.intersection_update(docs_with_concept)
            
            if not candidate_docs: break
        
        if not candidate_docs:
            print("   Aucun résultat.")
            continue

        results = []
        for url in candidate_docs:
            product_data = products_db.get(url, {})
            title = product_data.get("title", "")
            
            s_bm25 = ranking.bm25_score(expanded_tokens, url, title_index, doc_lengths, avg_dl, total_docs)
            s_reviews = reviews_index.get(url, {}).get('mean_mark', 0)
            s_title = ranking.title_match_score(original_tokens, title)
            s_pos = ranking.position_score(original_tokens, url, title_index)

            components = {"bm25": s_bm25, "reviews": s_reviews, "title": s_title, "position": s_pos}
            final_score = ranking.linear_score(components, config.WEIGHTS)
            
            results.append({"title": title, "score": round(final_score, 3), "details": components})

        results.sort(key=lambda x: x['score'], reverse=True)

        for i, res in enumerate(results[:3]):
            print(f"   {i+1}. {res['title']} (Score: {res['score']})")
            print(f"      Détails: BM25={round(res['details']['bm25'], 2)} | Avis={res['details']['reviews']} | Titre={round(res['details']['title'], 2)}")

if __name__ == "__main__" :
    test_config_parameters(products_db, title_index, origin_index, reviews_index, 
                       doc_lengths, avg_dl, total_docs, synonyms_map)