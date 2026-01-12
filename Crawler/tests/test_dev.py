import urllib

def validate_url(url):
    """Valide le format de l'URL"""
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def handle_crawl_error(url, error):
    """Gère les erreurs de crawling"""
    print(f"Erreur lors du crawling de {url}: {error}")

def log_progress(visited_count, max_pages, current_url):
    """Affiche la progression du crawling"""
    print(f"Crawling ({visited_count}/{max_pages}): {current_url}")

def test_different_start_urls():
    """
    Teste le crawler avec différentes URLs de départ
    Retourne une liste de configurations de test
    """
    return [
        {
            'name': 'Test 1 - Page produits',
            'url': 'https://web-scraping.dev/products',
            'max_pages': 50
        },
        {
            'name': 'Test 2 - Produit seul',
            'url': 'https://web-scraping.dev/product/1',
            'max_pages': 5
        },
        {
            'name': 'Test 3 - Accueil',
            'url': 'https://web-scraping.dev/',
            'max_pages': 5
        }
    ]