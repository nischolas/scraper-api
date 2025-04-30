import requests
from recipe_scrapers import scrape_html
import logging

class RecipeScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.headers = {
            "User-Agent": "Recipe Scraper API (https://github.com/your-username/recipe-api)"
        }

    def scrape(self, url):
        html = requests.get(url, headers=self.headers).content
        scraper = scrape_html(html, org_url=url)
        
        recipe_data = self._extract_core_data(scraper)
        self._add_optional_data(scraper, recipe_data)
        
        return recipe_data

    def _extract_core_data(self, scraper):
        yields = int(''.join(char for char in scraper.yields() if char.isdigit()))
        return {
            'title': scraper.title(),
            'total_time': scraper.total_time(),
            'yields': yields,
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
                self.logger.debug(f"Optional method {method_name} not available: {str(e)}")
