## Structures d'Index

### 1. Index Inversés Positionnels (title_index.json, description_index.json)

Utilisés pour les champs Titre et Description. Contrairement à un index inversé simple, cette structure stocke la position de chaque token dans le document, permettant une future implémentation de recherche de phrases ou de classement par proximité.

- **Clé** : Token (mot)

- **Valeur** : Dictionnaire où les clés sont les URLs de documents (IDs) et les valeurs sont des listes de positions.

- **Prétraitement** : Minuscules, suppression de la ponctuation, suppression des mots vides [`src/utils.py => tokenize()`].

#### Tokenisation

Pour garantir des index plus propres, la fonction `tokenize` dans `src/utils.py` applique le processus suivant :

- **Mise en minuscules** : Pour assurer l'insensibilité à la casse (ex : "Apple" == "apple").

- **Suppression de la ponctuation** : Tous les caractères dans `string.punctuation` sont supprimés.

- **Filtrage des mots vides** : Une liste personnalisée et minimale de mots vides anglais (ex : "the", "and", "is") est utilisée pour réduire la taille de l'index et le bruit.

**Exemple :**

```json
{
  "chocolate": {
    "https://web-scraping.dev/product/1": [2],
    "https://web-scraping.dev/product/5": [0, 5]
  },
  "box": {
    "https://web-scraping.dev/product/1": [0]
  }
}
```
---

### 2. Index de Caractéristiques (brand_index.json, origin_index.json)

Index inversés pour les caractéristiques catégorielles. LA tâche est d'extraire des clés spécifiques du dictionnaire `product_features` (en particulier "Brand" et "Made in").

- **Clé** : Valeur de caractéristique (normalisée en minuscules).

- **Valeur** : Liste des URLs de documents contenant cette caractéristique.

**Exemple (Marque) :**

```json
{
  "chocodelight": [
    "https://web-scraping.dev/product/1",
    "https://web-scraping.dev/product/13",
  ],
}
```
**Exemple (Origine) :**

```json
{
  "italy": [
    "https://web-scraping.dev/product/11",
    "https://web-scraping.dev/product/11?variant=black40",
    "https://web-scraping.dev/product/11?variant=black41",
  ],
  "usa": [
    "https://web-scraping.dev/product/12",
    "https://web-scraping.dev/product/12?variant=darkgrey-medium",
  ]
}
```

---

### 3. Index des Avis (reviews_index.json)

Un index direct (non inversé) stockant des métadonnées statistiques sur les avis produits. Il est utilisé pour classer/scorer les résultats plutôt que pour rechercher des mots-clés.

- **Clé** : URL du document.

- **Valeur** : Objet contenant :

  - `total_reviews` : Nombre d'avis.

  - `mean_mark` : Note moyenne (arrondie à 1 décimale).

  - `last_rating` : La note de l'avis le plus récent.

**Exemple :**

```json
{
  "https://web-scraping.dev/product/1": {
    "total_reviews": 5,
    "mean_mark": 4.6,
    "last_rating": 5
  },
}
```
---

## Script

### Générer les index

Pour générer les indexes il suffit d'exécuter dans le terminal la commande suivante :

```bash
python3 main.py
```
Si les dépendances de la librairie `nltk` manquent il faudrait rajouter dans un script python :
```python
nltk.download('stopwords')

nltk.download('punkt')
```

### Exécuter les Tests

Pour vérifier la logique (tokenisation, extraction, structure d'index) :

```bash
cd ./Index
python3 -m unittest tests/test_indexer.py
```
---