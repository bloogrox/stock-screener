import requests
from typing import Dict
from utils import cache, RedisStorage
import settings


def get_rates(token: str) -> Dict[str, float]:
    """
    returns: dict {'JPY': 114.01146, 'CNY': 6.40563, 'CHF': 0.91515}
    """
    url = f"https://freecurrencyapi.net/api/v2/latest?apikey={token}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()['data']


@cache(RedisStorage(settings.REDIS_URL), "rates", ttl=86400)
def cached_rates(token: str) -> Dict[str, float]:
    return get_rates(token)
