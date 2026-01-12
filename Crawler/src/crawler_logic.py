from collections import deque

def initialize_queue(start_url):
    """Initialise la file d'attente avec l'URL de départ"""
    return deque([start_url])

def has_reached_limit(visited, max_pages):
    """Vérifie si la limite de pages visitées est atteinte"""
    return len(visited) >= max_pages

def prioritize_url(url):
    """Détermine si une URL contient 'product' pour la priorisation"""
    return 'product' in url.lower()

def add_urls_to_queue(queue, visited, urls):
    """Ajoute des URLs à la file avec système de priorité"""
    priority_urls = []
    normal_urls = []
    
    for url in urls:
        if url not in visited and url not in queue:
            if prioritize_url(url):
                priority_urls.append(url)
            else:
                normal_urls.append(url)

    for url in priority_urls:
        queue.appendleft(url)

    for url in normal_urls:
        queue.append(url)
