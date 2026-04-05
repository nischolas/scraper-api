import requests
from recipe_scrapers import scrape_html
import logging

SCRAPER_HEADERS = {
    "User-Agent": "Recipe Scraper API (https://github.com/your-username/recipe-api)"
}

class RecipeScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def scrape(self, url):
        self.logger.info(f"Scraping URL: {url}")
        response = requests.get(url, headers=SCRAPER_HEADERS, timeout=10)
        response.raise_for_status()
        scraper = scrape_html(response.content, org_url=url)
        recipe_data = self._extract_core_data(scraper)
        self._add_optional_data(scraper, recipe_data)
        return recipe_data

    def _parse_yields(self, raw):
        digits = ''.join(char for char in raw if char.isdigit())
        return int(digits) if digits else None

    def _extract_core_data(self, scraper):
        return {
            'title': scraper.title(),
            'total_time': scraper.total_time(),
            'yields': self._parse_yields(scraper.yields()),
            'ingredients': scraper.ingredients(),
            'instructions': scraper.instructions(),
            'host': scraper.host(),
            'image': scraper.image()
        }

    def _add_optional_data(self, scraper, recipe_data):
        optional_methods = {
            'ingredient_groups': scraper.ingredient_groups,
            'instructions_list': scraper.instructions_list,
            'canonical_url': scraper.canonical_url,
            'keywords': scraper.keywords,
        }
        for method_name, method in optional_methods.items():
            try:
                result = method()
                if result:
                    recipe_data[method_name] = result
            except Exception as e:
                self.logger.debug(f"Optional method {method_name} not available: {e}")