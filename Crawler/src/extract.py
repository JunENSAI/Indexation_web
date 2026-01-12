from bs4 import BeautifulSoup
import urllib.parse

def can_fetch(robot_parser, url):
    """Vérifie si le crawler a le droit de parser une page"""
    return robot_parser.can_fetch("*", url)

def parse_html(html, url):
    """Parse le HTML et extrait titre, premier paragraphe et liens"""
    soup = BeautifulSoup(html, 'html.parser')
    
    title = extract_title(soup)
    description = extract_description(soup)
    links = extract_links(soup, url)
    
    return {
        'url': url,
        'title': title,
        'description': description,
        'links': links
    }

def extract_title(soup):
    """Extrait le titre de la page"""
    title = soup.find('title')
    return title.get_text().strip() if title else ""

def extract_description(soup):
    """Extrait le premier paragraphe de la page (description)"""
    first_paragraph = soup.find('p')
    return first_paragraph.get_text().strip() if first_paragraph else ""

def extract_links(soup, base_url):
    """Extrait tous les liens internes du body"""
    links = []
    parsed_base = urllib.parse.urlparse(base_url)
    
    body = soup.find('body')
    if not body:
        return links
    
    for link in body.find_all('a', href=True):
        href = link['href']
        absolute_url = urllib.parse.urljoin(base_url, href)
        parsed_url = urllib.parse.urlparse(absolute_url)
        
        if parsed_url.netloc == parsed_base.netloc:
            clean_url = urllib.parse.urlunparse(
                (parsed_url.scheme, parsed_url.netloc, parsed_url.path,
                 parsed_url.params, parsed_url.query, '')
            )
            links.append(clean_url)
    
    return links