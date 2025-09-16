import requests_cache

from weather.typer_functions import app

ONE_DAY = 86400
requests_cache.install_cache("cache.db", backend="sqlite", expire_after=ONE_DAY)

if __name__ == "__main__":
    app()
