# Moteur de Recherche (TP3)

Ce projet implémente un moteur de recherche textuel complet capable d'indexer des produits, de gérer des requêtes multilingues (Français/Anglais) grâce à une expansion par synonymes, et de classer les résultats par pertinence (BM25) et popularité (Avis).

---

## Architecture du Projet

```text
Engine/
├── main.py                   # Point d'entrée : Chargement, Boucle de recherche, Affichage
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

### 1. Gestion des Synonymes (Augmentation de Requête)

* **Problème :** L'utilisateur tape "baskets bleu" mais l'index ne contient que "sneakers" et "blue". C'est le problème du silence. Solution :

* **Fusion des dictionnaires :** Nous combinons origin_synonyms.json et product_synonyms.json en un dictionnaire plus complets.

* **Logique Bidirectionnelle (Aplatissement) :** Si sneakers est synonyme de baskets, alors chercher baskets renvoie aussi sneakers.

* **Traduction Implicite :** Les fichiers contiennent des mappages Français -> Anglais (ex: bleu -> blue), permettant de requêter en français sur un index anglais.

### 2. Stratégie de Filtrage

* **Approche (OR local + AND global)** : Le moteur décompose la requête "baskets bleu" en concepts :

    * Concept 1 (Objet) : baskets OU sneakers OU shoes ...

    * Concept 2 (Couleur) : bleu OU blue ...

    * Résultat : Intersection (Concept 1 ∩ Concept 2). Cela garantit un Rappel (Recall) maximal sans sacrifier la précision.

### 3. Ranking Hybride (BM25 + Avis)

Pour trier les résultats, nous ne nous basons pas uniquement sur la présence des mots, mais sur un score composé :

* **BM25 (Poids 0.7)** : Algorithme probabiliste standard qui favorise les documents où les termes rares apparaissent fréquemment, tout en pénalisant les documents très longs.

* **Note** : La longueur des documents est calculée précisément via `rearranged_products.jsonl`.

* **Score Avis (Poids 0.3)** : Utilisation de la note moyenne (mean_mark) pour faire remonter les produits populaires ("Quality Bias").

---

## Exemple de resultat de recherche

Voici la preuve du fonctionnement sur une requête complexe ("baskets bleu") mélangeant argot/français et nécessitant une recherche géographique et sémantique :

```Plaintext
Entrez votre recherche (ex: 'blue usa') : baskets bleu
   Concepts traités : ['baskets', 'bleu']
   Documents candidats : 4

 4 Résultats trouvés :

1. Kids' Light-Up Sneakers - Blue 6 (Score: 4.1929)
   Origine: Usa | URL: [https://web-scraping.dev/product/22?variant=blue-6](https://web-scraping.dev/product/22?variant=blue-6)

2. Kids' Light-Up Sneakers - Blue 6 (Score: 4.1436)
   Origine: India | URL: [https://web-scraping.dev/product/10?variant=blue-6](https://web-scraping.dev/product/10?variant=blue-6)

3. Kids' Light-Up Sneakers - Blue 5 (Score: 4.1196)
   Origine: France | URL: [https://web-scraping.dev/product/22?variant=blue-5](https://web-scraping.dev/product/22?variant=blue-5)

4. Kids' Light-Up Sneakers - Blue 5 (Score: 4.1196)
   Origine: Netherlands | URL: [https://web-scraping.dev/product/10?variant=blue-5](https://web-scraping.dev/product/10?variant=blue-5)
```

On constate que le moteur a correctement traduit "baskets" en "sneakers" et "bleu" en "blue", tout en récupérant les origines depuis l'index dédié.

---