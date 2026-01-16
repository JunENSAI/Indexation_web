# Moteur de Recherche (TP3)

Ce projet implémente un moteur de recherche textuel complet capable d'indexer des produits, de gérer des requêtes multilingues (Français/Anglais) grâce à une expansion par synonymes, et de classer les résultats par pertinence (BM25) et popularité (Avis).

---

## Architecture du Projet

```text
Engine/
├── main.py                   # Point d'entrée : Chargement, Boucle de recherche, Affichage
├── test_config.py            # Test les paramètre de configuration (poids Bm25, poids reviews,...)
└── input/
    ├── rearranged_products.jsonl # Base de données "Document Store" (Titre, Desc, URL...)
    ├── title_index.json          # Index inversé (Mots -> URLs)
    ├── origin_index.json         # Index des origines (Pays -> URLs)
    ├── reviews_index.json        # Index des métadonnées (Notes, Nombre d'avis)
    ├── origin_synonyms.json      # Synonymes géographiques (usa -> united states)
    ├── product_synonyms.json     # Synonymes produits (baskets -> sneakers)
└── src/
    ├── __init__.py
    ├── config.py             # Configuration (Poids, Hyperparamètres BM25)
    ├── preprocessing.py      # Tokenization, Stopwords, Fusion des Synonymes
    ├── ranking.py            # Calculs BM25 et Scoring Linéaire
    └── utils.py              # Chargement des fichiers JSON/JSONL
```
---

## Details de l'implémentation

Le details de l'implémentation englobe le flux d'éxecution dans le fichier `main.py`.

### 1. Initialisation et Chargement

Avant d'entrer dans la boucle de recherche, le programme charge toutes les ressources nécessaires en mémoire pour garantir la rapidité des réponses.
* **Ressources NLTK** : Initialisation des outils linguistiques et chargement des *stopwords*.

* **Indexes Inversés** : Chargement des fichiers JSON (`title_index`, `origin_index`, `reviews_index`).

* **Base de Produits** : Chargement de `products.jsonl` pour accéder aux données brutes (titres, descriptions) nécessaires à l'affichage.

* **Pré-calculs** :
    * Création d'une map `url_to_origin` pour un accès rapide au pays d'origine d'un produit.

    * Calcul des statistiques du corpus (`avg_dl`, `doc_lengths`) via `ranking.compute_stats`, indispensables pour le score BM25.

    * Fusion des dictionnaires de synonymes (produits + origines) en une seule map.

### 2. Gestion des Synonymes (Augmentation de Requête)

* **Problème :** L'utilisateur tape "baskets bleu" mais l'index ne contient que "sneakers" et "blue". C'est le problème du silence. Solution :

* **Fusion des dictionnaires :** Nous combinons origin_synonyms.json et product_synonyms.json en un dictionnaire plus complets.

* **Logique Bidirectionnelle (Aplatissement) :** Si sneakers est synonyme de baskets, alors chercher baskets renvoie aussi sneakers.

* **Traduction Implicite :** Les fichiers contiennent des mappages Français -> Anglais (ex: bleu -> blue), permettant de requêter en français sur un index anglais.

### 3. Stratégie de Filtrage

* **Approche (OR local + AND global)** : Le moteur décompose la requête "baskets bleu" en concepts :

    * Concept 1 (Objet) : baskets OU sneakers OU shoes ...

    * Concept 2 (Couleur) : bleu OU blue ...

    * Résultat : Intersection (Concept 1 ∩ Concept 2). Cela garantit un Rappel (Recall) maximal sans sacrifier la précision.

### 4. Ranking

Le tri final repose sur une combinaison linéaire de quatre signaux distincts, permettant d'équilibrer la pertinence sémantique et la popularité :

* **BM25 (Poids 0.6)** :
    Algorithme probabiliste qui constitue le cœur du moteur. Il favorise les documents où les termes rares apparaissent fréquemment, tout en normalisant selon la longueur du document (paramètres $k_1=1.2, b=0.75$).

    $$ Bm25(q, D, b, k) = \sum_{i=1}^{n} IDF(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{avgdl}\right)} $$

* **Score Titre (Poids 0.4)** :
    * **Approche :** Nous calculons un score spécifique si les termes de la requête apparaissent dans le champ `title`.

    * **Justification :** Le titre étant un résumé dense du produit, une correspondance ici est un signal de pertinence bien plus fort qu'une mention dans une longue description.

* **Score Avis (Poids 0.3)** :

   Utilisation de la note moyenne (`mean_mark`) pour introduire un "Quality Bias", faisant remonter légèrement les produits plébiscités par les utilisateurs.

* **Score de Position (Poids 0.1)** :
    * **Approche :** Utilisation de l'index positionnel pour valoriser l'emplacement des mots.

    * **Calcul :** Nous appliquons une décroissance logarithmique $$score = 1 / (1 + \ln(position))$$
    
    * **Justification :** Les mots clés les plus importants apparaissent généralement au tout début du titre ou de la description. Ce score sert de bonus pour départager des documents similaires.

---

## Test des paramètres de configuration

Nous avons évalué le moteur via un script de test automatisé couvrant des cas multilingues et spécifiques.

### Analyse des résultats
* **Expansion de requête (`basket bleu`)** : Le test est concluant. Le moteur retrouve les produits anglais ("Sneakers") grâce au dictionnaire de synonymes, validant l'efficacité du score BM25 (poids 0.6) pour la recherche sémantique.

* **Analyse du cas (`Cat-Ear`)** : Nous avons observé une discordance de tokenization. Le produit est stocké dans l'index sous la clé normalisée `catear` (concaténé), alors que le tokenizer standard découpe la requête en deux tokens `['cat', 'ear']`. Sans modification du tokenizer, ce cas nécessite l'ajout d'une entrée dans le dictionnaire de synonymes pour faire le pont (`cat-ear` -> `catear`).

* **Équilibre des poids** : Les tests confirment que la popularité (Avis) ne doit servir que de bonus mineur.

### Configuration 

| Paramètre | Valeur | Justification |
| :--- | :--- | :--- |
| **BM25** | **0.6** | Composante majeure pour garantir la pertinence du sujet. |
| **Titre** | **0.4** | Privilégie les documents dont le sujet est explicite dans le titre. |
| **reviews** | **0.3** | Les produits bien notés contribuent dans le score final. |

## Exemple de résultat de recherche

```json
{
  "metadata": {
    "query": "basket bleu",
    "nombre_total_doc": 156,
    "doc_filtre": 51
  },
  "results": [
    {
      "title": "Running Shoes for Men - 12",
      "url": "https://web-scraping.dev/product/9?variant=12",
      "description": "Stay comfortable during your runs with our men's running shoes. The durable outsole offers solid traction, ensuring stability even on slippery surfaces. Featuring a breathable upper and a cushioned midsole, these shoes provide excellent ventilation and shock absorption",
      "score": 4.556,
      "details": {
        "bm25": 5.494,
        "reviews": 4.2,
        "title": 0.0,
        "position": 0.0
      }
    }
  ]
}
```

**Analyse du résultat :**

- Pertinence Sémantique : On constate que le moteur a correctement traduit "baskets" en "sneakers" via le dictionnaire de synonymes, trouvant ainsi des documents pertinents malgré l'absence des mots exacts dans le titre `(Score Titre = 0.0)`.

- Ranking : Le score final (`4.556`) est principalement porté par le BM25 (`5.494`), validant l'importance de ce signal pour les recherches thématiques.


---