from flask import Flask, request, jsonify
import logging
from logging.handlers import TimedRotatingFileHandler
import os
from urllib.parse import urlparse
import requests
from recipe_scrapers import scrape_html
from datetime import datetime

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Set up logging
app = Flask(__name__)

# Add this to handle running behind a proxy
app.config['PREFERRED_URL_SCHEME'] = 'https'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Console handler (for seeing logs in terminal)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)

# File handler (for logging to file with rotation)
file_handler = TimedRotatingFileHandler(
    filename='logs/recipe_api.log',
    when='midnight',
    interval=1,
    backupCount=7,
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)
file_format = logging.Formatter(
    '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
file_handler.setFormatter(file_format)
logger.addHandler(file_handler)

# Add a health check endpoint
@app.route('/')
def health_check():
    return jsonify({"status": "healthy", "message": "Recipe scraper API is running"}), 200

@app.route('/scrape', methods=['POST'])
def scrape_recipe():
    try:
        request_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.debug(f"[{request_time}] Received request: {request.get_data(as_text=True)}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        
        # Parse JSON data
        try:
            data = request.get_json(force=True)
            logger.debug(f"Parsed JSON data: {data}")
        except Exception as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return jsonify({'error': 'Invalid JSON format'}), 400

        # Check for URL
        if not data or 'url' not in data:
            logger.error("No URL provided in request data")
            return jsonify({'error': 'No URL provided'}), 400
            
        url = data['url']
        logger.info(f"Processing URL: {url}")
        
        # Validate URL
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                logger.error(f"Invalid URL format: {url}")
                return jsonify({'error': 'Invalid URL format'}), 400
        except Exception as e:
            logger.error(f"URL parsing error: {str(e)}")
            return jsonify({'error': 'Invalid URL'}), 400

        # Fetch HTML content
        logger.info("Fetching recipe page")
        headers = {
            "User-Agent": "Recipe Scraper API (https://github.com/your-username/recipe-api)"
        }
        html = requests.get(url, headers=headers).content
        
        # Scrape recipe
        logger.info("Starting recipe scrape")
        scraper = scrape_html(html, org_url=url)
        
        # Extract recipe data with error handling for each method
        recipe_data = {}
        
        # Required methods (these should always work)
        try:
            recipe_data.update({
                'title': scraper.title(),
                'total_time': scraper.total_time(),
                'yields': scraper.yields(),
                'ingredients': scraper.ingredients(),
                'instructions': scraper.instructions(),
                'host': scraper.host(),
                'image': scraper.image()
            })
        except Exception as e:
            logger.error(f"Error extracting core recipe data: {str(e)}")
            return jsonify({'error': 'Failed to extract core recipe data'}), 500

        # Optional methods (might not be available for all recipes)
        # optional_methods = {
        #     'ingredient_groups': scraper.ingredient_groups,
        #     'instructions_list': scraper.instructions_list,
        #     'nutrients': scraper.nutrients,
        #     'canonical_url': scraper.canonical_url,
        #     'equipment': scraper.equipment,
        #     'cooking_method': scraper.cooking_method,
        #     'keywords': scraper.keywords,
        #     'dietary_restrictions': scraper.dietary_restrictions,
        #     'links': scraper.links
        # }

        # for method_name, method in optional_methods.items():
        #     try:
        #         result = method()
        #         if result:  # Only add if there's actual data
        #             recipe_data[method_name] = result
        #     except Exception as e:
        #         logger.debug(f"Optional method {method_name} not available: {str(e)}")
                
        logger.info("Successfully scraped recipe")
        return jsonify(recipe_data)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting Recipe Scraper API on port {port}")
    app.run(host='0.0.0.0', port=port)