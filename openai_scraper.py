import requests
from bs4 import BeautifulSoup
import openai
import logging
from typing import Optional
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
from pydantic import BaseModel

SCRAPER_HEADERS = {
    "User-Agent": "Recipe Scraper API (https://github.com/your-username/recipe-api)"
}

class RecipeResponse(BaseModel):
    total_time: Optional[int] = None
    yields: Optional[int] = None
    ingredients: list[str]
    keywords: list[str]
    instructions: str
    instructions_list: list[str]

class OpenAIRecipeScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        load_dotenv()
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def scrape(self, url: str) -> dict:
        self.logger.info(f"Scraping URL with OpenAI: {url}")
        response = requests.get(url, headers=SCRAPER_HEADERS, timeout=10)
        response.raise_for_status()

        html = response.content
        soup = BeautifulSoup(html, 'html.parser')

        main_content = self._extract_main_content(soup)
        og_image = soup.find('meta', property='og:image')
        og_title = soup.find('meta', property='og:title')
        og_url = soup.find('meta', property='og:url')

        system_prompt = """
        Du bist ein Experte für die Extraktion von Rezepten aus HTML-Code.
        Extrahiere die Rezeptinformationen aus dem bereitgestellten Text.
        Wenn das Rezept in einer anderen Sprache als Deutsch ist, übersetze es ins Deutsche
        und konvertiere imperiale in metrische Einheiten bei Bedarf.
        Stelle sicher dass instructions_list eine Liste von einzelnen Schritten ist,
        und instructions die gleichen Schritte als ein String mit '\\n' als Trenner.
        """

        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": main_content}
            ],
            response_format=RecipeResponse,
        )

        recipe = completion.choices[0].message.parsed

        return {
            **recipe.model_dump(),
            'canonical_url': og_url.get('content') if og_url else None,
            'host': self._extract_domain(url),
            'image': og_image.get('content') if og_image else None,
            'title': og_title.get('content') if og_title else None,
        }

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', {'class': ['content', 'main', 'recipe']})
        )
        if main_content:
            return main_content.get_text(separator='\n', strip=True)
        return soup.get_text(separator='\n', strip=True)

    def _extract_domain(self, url: str) -> str:
        return urlparse(url).hostname.replace('www.', '')