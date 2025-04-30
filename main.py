from flask import Flask, request, jsonify
import logging
from flask_cors import CORS
from recipe_scraper import RecipeScraper
from openai_scraper import OpenAIRecipeScraper
from utils import setup_logging, validate_url

app = Flask(__name__)
logger = setup_logging()
CORS(app, resources={
    r"/scrape": {
        "origins": ["http://localhost:5173","http://192.168.0.194:5173", "mbpvn.local:5173"],
        "methods": ["POST"],
        "allow_headers": ["Content-Type"]
    }
})

@app.route('/scrape', methods=['POST'])
def scrape_recipe():
    try:
        logger.debug(f"Received request: {request.get_data(as_text=True)}")
        
        try:
            data = request.get_json(force=True)
            logger.debug(f"Parsed JSON data: {data}")
        except Exception as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return jsonify({'error': 'Invalid JSON format'}), 400

        if not data or 'url' not in data:
            logger.error("No URL provided in request data")
            return jsonify({'error': 'No URL provided'}), 400
            
        url = data['url']
        if not validate_url(url):
            return jsonify({'error': 'Invalid URL format'}), 400

        # Try standard recipe scraping first
        recipe_scraper = RecipeScraper()
        try:
            recipe_data = recipe_scraper.scrape(url)
            logger.info("Successfully scraped recipe using standard scraper")
            return jsonify(recipe_data)
        except Exception as e:
            logger.warning(f"Standard scraping failed: {str(e)}, attempting OpenAI fallback")
            
            # Fallback to OpenAI
            openai_scraper = OpenAIRecipeScraper()
            try:
                recipe_data = openai_scraper.scrape(url)
                logger.info("Successfully scraped recipe using OpenAI")
                return jsonify(recipe_data)
            except Exception as e:
                logger.error(f"OpenAI scraping failed: {str(e)}")
                return jsonify({'error': 'Failed to extract recipe data'}), 500

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
