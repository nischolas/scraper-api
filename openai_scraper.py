import requests
from bs4 import BeautifulSoup
import openai
import logging
from typing import Dict, Any
import json
import os
from dotenv import load_dotenv
from urllib.parse import urlparse


class OpenAIRecipeScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.headers = {
            "User-Agent": "Recipe Scraper API (https://github.com/your-username/recipe-api)"
        }
        load_dotenv()
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )

    def scrape(self, url: str) -> Dict[str, Any]:
        html = requests.get(url, headers=self.headers).content
        main_content = self._extract_main_content(html)
        soup = BeautifulSoup(html, 'html.parser')
        og_image = soup.find('meta', property='og:image')
        og_title = soup.find('meta', property='og:title')
        og_url = soup.find('meta', property='og:url')
        
        system_prompt = """
        Du bist ein Experte für die Extraktion von Rezpten aus HTML-Code. Bitte extrahiere die Rezeptinformationen aus dem bereitgestellten HTML-Code und gib ihn in folgendem JSON-Format zurück:
        {
            "total_time": Zahl in Minuten,
            "yields": Zahl in Portionen,
            "ingredients": ["Liste", "der", "Zutaten"],
            "keywords": ["Liste", "der", "Keywords"],
            "instructions": "Anleitung des Rezeptes, mit Schritten falls vorhanden and absätzen in Form von '\\n'"
        }

        Wenn das Rezept in einer anderen Sprache als deutsch ist, bitte übersetze in deutsch (und konvertiere imperiale in metrische Einheiten bei Bedarf)
        
        Bitte stelle sicher:
        1. Nur valides JSON
        2. Zutaten und Keywords als Array
        3. Stelle sicher dass es instructions und instructions_list gibt
        """

        # "instructions_list": ["Schritt 1", "Schritt 2", "..."],
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": main_content}
            ],
            response_format={ "type": "json_object" }
        )
        
        # Parse the JSON response
        try:
            recipe_data = json.loads(response.choices[0].message.content)
            recipe_data['canonical_url'] = og_url.get('content')
            recipe_data['host'] = self._extract_domain(url)
            recipe_data['image'] = og_image.get('content')
            recipe_data['title'] = og_title.get('content')
            self.logger.info(recipe_data)
            return recipe_data
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse OpenAI response as JSON: {e}")
            raise Exception("Failed to parse recipe data")

    def _extract_main_content(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')

        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()
            
        main_content = soup.find('main') or soup.find('article') or soup.find('div', {'class': ['content', 'main', 'recipe']})

        if main_content:                
            return main_content.get_text(separator='\n', strip=True)
        
        return soup.get_text(separator='\n', strip=True)
    
    def _extract_domain(self, url: str) -> str:
        parsed_url = urlparse(url)
        return parsed_url.hostname.replace('www.', '')