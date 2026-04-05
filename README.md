# Flask app based on [hhursev/recipe_scrapers](https://github.com/hhursev/recipe-scrapers)

uv run main.py

Example request

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.chefkoch.de/rezepte/79211030371728/Restetorte.html"}' \
  http://localhost:8000/scrape
```

Unsupportd URL but works with openAI:
https://www.einfachkochen.de/rezepte/ueberbackene-maultaschen-einfach-schnell
