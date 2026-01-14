# Indexation_web

Ce dépôt contient l'ensemble du code développé pour le cours d'Indexation Web. L'objectif final est de construire un moteur de recherche, partant de la collecte des données jusqu'à l'interface de recherche utilisateur.

## TP1 : Crawling & Collecte de Données

### Objectif : 

**Développer un "crawler" (robot d'indexation) capable de naviguer sur un site e-commerce cible (https://web-scraping.dev/products) pour extraire les informations des produits de manière automatique et respectueuse.**

### Contenu

Le script de crawling implémente les fonctionnalités suivantes :

- Respect du `robots.txt` : Implémentation d'une fonction pour vérifier les autorisations d'accès avant de crawler.

- **Gestion de la frontière** : Utilisation d'une file d'attente (FIFO) pour gérer les URLs à visiter via get_uncrawled_urls, en évitant les boucles infinies et les doublons.

- **Extraction HTML** : Utilisation de requests pour le téléchargement et BeautifulSoup pour le parsing.

- **Extraction de données structurées** : Une fonction qui capture pour chaque produit : 

    - Le titre
    
    - La descriptionLes variantes (couleurs, tailles) via les paramètres d'URL.

    - Les liens (et informations des URL)

- **Stockage** : Sauvegarde incrémentale des données dans un fichier products.jsonl (JSON Lines).

- **Notion de politesse** : Ajout d'un délai d'attente (time.sleep) entre les requêtes pour ne pas surcharger le serveur.

---

## TP2 : Construction d'index

### Objectif : 

**Transformer les données brutes collectées au TP1 (products.jsonl) en structures de données optimisées pour la recherche (index inversés).**

### Contenu 

Ce module se charge de l'indexation via les étapes suivantes :

- **Tokenization** : Nettoyage du texte (minuscule, suppression de la ponctuation) pour uniformiser les termes via la fonction tokenize.

- **Création des Index** : Développement de fonctions pour générer plusieurs types d'index :

    - `title_index.json` : Index inversé positionnel sur les titres des produits.

    - `description_index.json` : Index inversé positionnel sur les descriptions (similaire au titre).
    
    - `reviews_index.json` : Index non-positionnel stockant les métadonnées des avis (note moyenne, nombre d'avis) pour le ranking.
    
    - `origin_index.json` : Index inversé reliant les pays d'origine aux URLs des produits.

---

## TP3 : Moteur de Recherche & Ranking

### Objectif : 

**Développer l'interface de recherche qui utilise les index du TP2 pour traiter les requêtes utilisateurs et retourner les résultats les plus pertinents.**

### Contenu

Le moteur de recherche intègre les composants suivants :

* **Prétraitement de la requête** : 

    * Tokenization identique à celle de l'indexation.

    * Augmentation par synonymes : Enrichissement de la requête (ex: "baskets" → "baskets, sneakers, tennis") via une fusion de dictionnaires (Produits + Pays).

    * Filtrage des "stop words" (mots vides) pour ne garder que les concepts importants.

    * Filtrage des documents (Matching) :Application d'une logique booléenne hybride : OR entre les synonymes d'un même concept, et AND entre les différents concepts de la requête.

* **Métrique et interface** :

    * Ranking (Classement) : Score BM25 : Implémentation de la fonction probabiliste Okapi BM25 pour évaluer la pertinence textuelle (basée sur la fréquence des termes et la longueur des documents).

    * Score de Popularité : Intégration des notes clients (Reviews) issues de reviews_index.json.

    * Score Final : Combinaison linéaire : $Score = w_1 \cdot BM25 + w_2 \cdot Avis$.

    * Interface Utilisateur :Boucle interactive dans le terminal permettant de saisir des mots-clés.Affichage structuré des résultats (Titre, URL, Origine, Score).

---
