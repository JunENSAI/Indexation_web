import time
from src.config import setup_robot_parser, fetch_page
from tests.test_dev import validate_url, log_progress, handle_crawl_error, test_different_start_urls
from src.storage import save_to_json
from src.crawler_logic import initialize_queue, has_reached_limit, add_urls_to_queue
from src.extract import can_fetch, parse_html

def main():
    test_configs = test_different_start_urls()

    for i, config in enumerate(test_configs, 1):
        
        current_url = config['url']
        max_pages = config['max_pages']
        
        print(f"\n{'='*70}")
        print(f"Lancement {config['name']}")
        print(f"URL: {current_url}")
        print(f"{'='*70}")

        if not validate_url(current_url):
            print(f"URL invalide pour ce test: {current_url}")
            continue

        robot_parser = setup_robot_parser(current_url)
        queue = initialize_queue(current_url)
        visited = set()
        results = []

        while queue and not has_reached_limit(visited, max_pages):
            url = queue.popleft()
            
            if url in visited:
                continue
            
            if not can_fetch(robot_parser, url):
                print(f"Interdit par robots.txt: {url}")
                continue
            
            log_progress(len(visited) + 1, max_pages, url)
            
            html = fetch_page(url)
            if not html:
                continue
            
            try:
                data = parse_html(html, url)
                results.append(data)
                visited.add(url)
                
                add_urls_to_queue(queue, visited, data['links'])
                
                time.sleep(0.5)               
            except Exception as e:
                handle_crawl_error(url, e)
        filename = f"products_test_{i}.json"
        save_to_json(results, filename)

if __name__ == "__main__":
    main()