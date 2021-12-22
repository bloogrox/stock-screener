docker-compose run --rm app python load_prices.py
docker-compose run --rm app python recalc_metrics.py
docker-compose run --rm app python screener.py
