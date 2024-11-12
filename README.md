# Recipe Scraper based on [hhursev/recipe_scrapers](https://github.com/hhursev/recipe-scrapers)

Create virtual environment

```bash
python3 -m venv venv
```

Enter environment

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip3 install -r requirements.txt
```

Run server

```bash
python3 app.py
```

Example request

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.chefkoch.de/rezepte/79211030371728/Restetorte.html"}' \
  http://localhost:8000/scrape
```
