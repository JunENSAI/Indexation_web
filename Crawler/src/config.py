import urllib.request
import urllib.robotparser
import urllib.parse

def setup_robot_parser(start_url):
    """Configure le parser robots.txt"""
    robot_parser = urllib.robotparser.RobotFileParser()
    parsed = urllib.parse.urlparse(start_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    robot_parser.set_url(robots_url)
    try:
        robot_parser.read()
    except:
        pass
    return robot_parser

def fetch_page(url):
    """Requête HTTP pour récupérer le contenu d'une page"""
    try:
        headers = {'User-Agent': 'JunENSAI'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Erreur lors du fetch de {url}: {e}")
        return None
