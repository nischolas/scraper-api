from flask import Flask, request, jsonify
import logging
import os
from flask_cors import CORS
from recipe_scraper import RecipeScraper
from openai_scraper import OpenAIRecipeScraper
from utils import setup_logging, validate_url
from config import ALLOWED_ORIGINS

app = Flask(__name__)
logger = setup_logging()

CORS(app, resources={
    r"/scrape": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["POST"],
        "allow_headers": ["Content-Type"]
    }
})

recipe_scraper = RecipeScraper()
openai_scraper = OpenAIRecipeScraper()

@app.route('/scrape', methods=['POST'])
def scrape_recipe():
    logger.debug(f"Received request: {request.get_data(as_text=True)}")

    data = request.get_json(force=True, silent=True)
    if not data:
        logger.error("Invalid or missing JSON in request")
        return jsonify({'error': 'Invalid JSON format'}), 400
    if 'url' not in data:
        logger.error("No URL provided in request data")
        return jsonify({'error': 'No URL provided'}), 400
    if not validate_url(data['url']):
        return jsonify({'error': 'Invalid URL format'}), 400

    url = data['url']

    try:
        recipe_data = recipe_scraper.scrape(url)
        logger.info("Successfully scraped recipe using standard scraper")
        return jsonify(recipe_data)
    except Exception as e:
        logger.warning(f"Standard scraping failed: {e}, trying OpenAI fallback")

    try:
        recipe_data = openai_scraper.scrape(url)
        logger.info("Successfully scraped recipe using OpenAI")
        return jsonify(recipe_data)
    except Exception as e:
        logger.error(f"OpenAI scraping failed: {e}")
        return jsonify({'error': 'Failed to extract recipe data'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true')