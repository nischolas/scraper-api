from flask import Flask, request, jsonify
import logging
from urllib.parse import urlparse
import requests
from recipe_scrapers import scrape_html

app = Flask(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.route('/scrape', methods=['POST'])
def scrape_recipe():
    try:
        logger.debug(f"Received request: {request.get_data(as_text=True)}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        
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
        logger.info(f"Processing URL: {url}")
        
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                logger.error(f"Invalid URL format: {url}")
                return jsonify({'error': 'Invalid URL format'}), 400
        except Exception as e:
            logger.error(f"URL parsing error: {str(e)}")
            return jsonify({'error': 'Invalid URL'}), 400

        logger.info("Fetching recipe page")
        headers = {
            "User-Agent": "Recipe Scraper API (https://github.com/your-username/recipe-api)"
        }
        html = requests.get(url, headers=headers).content
        
        logger.info("Starting recipe scrape")
        scraper = scrape_html(html, org_url=url)
        
        recipe_data = {}
        
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

        optional_methods = {
            'ingredient_groups': scraper.ingredient_groups,
            'instructions_list': scraper.instructions_list,
            # 'nutrients': scraper.nutrients,
            'canonical_url': scraper.canonical_url,
            # 'equipment': scraper.equipment,
            # 'cooking_method': scraper.cooking_method,
            'keywords': scraper.keywords,
            # 'dietary_restrictions': scraper.dietary_restrictions,
            # 'links': scraper.links
        }

        for method_name, method in optional_methods.items():
            try:
                result = method()
                if result:
                    recipe_data[method_name] = result
            except Exception as e:
                logger.debug(f"Optional method {method_name} not available: {str(e)}")
                
        logger.info("Successfully scraped recipe")
        return jsonify(recipe_data)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
