import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class Scraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }

    def scrape_list_page(self, url):
        """
        Scrapes a list page for blueprint links and titles.
        Returns a list of dictionaries with 'title', 'href', and the 'next_page_url'.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            blueprints = []
            rows = soup.select('li.list__row--data')
            for row in rows:
                title_div = row.select_one('div[data-name="Title"]')
                if title_div:
                    title_link = title_div.select_one('a.list__link')
                    title = title_link.get_text(strip=True) if title_link else title_div.get_text(strip=True)
                    href = title_link.get('href') if title_link else None
                    
                    # Extract ID from href (e.g., /blueprint/yb5yfb_z/ -> yb5yfb_z)
                    bp_id = None
                    if href:
                        parts = href.strip('/').split('/')
                        if len(parts) >= 2:
                            bp_id = parts[-1]
                            
                    blueprints.append({'title': title, 'href': href, 'id': bp_id})
            
            next_page_url = None
            next_page_link = soup.select_one('a[aria-label="Next page"]')
            if next_page_link and next_page_link.get('href'):
                next_page_path = next_page_link.get('href')
                next_page_url = urljoin(url, next_page_path)
            
            return blueprints, next_page_url
            
        except requests.exceptions.RequestException as e:
            print(f"Error during list scraping: {e}")
            return [], None

    def scrape_detail_page(self, url):
        """
        Scrapes a detail page for the blueprint code.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            detail_soup = BeautifulSoup(response.content, 'html.parser')
            
            code_textarea = detail_soup.select_one('textarea#code_to_copy')
            if code_textarea:
                return code_textarea.get_text(strip=True)
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching detail page: {e}")
            return None
