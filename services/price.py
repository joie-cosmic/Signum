import requests
import os


def get_coin_data(coin_id: str) -> dict:
    """Get current price and 24h change for a coin."""
    api_key = os.getenv('COINGECKO_API_KEY')

    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',
        'ids': coin_id,
        'sparkline': False,
        'x_cg_demo_api_key': api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    if not data:
        return None

    coin = data[0]
    return {
        'id': coin['id'],
        'name': coin['name'],
        'symbol': coin['symbol'].upper(),
        'price': coin['current_price'],
        'change_24h': coin['price_change_percentage_24h'],
        'market_cap': coin['market_cap'],
        'volume_24h': coin['total_volume'],
        'image': coin['image']
    }


def search_coin(query: str) -> str:
    """Search for a coin and return its CoinGecko ID."""
    api_key = os.getenv('COINGECKO_API_KEY')

    url = 'https://api.coingecko.com/api/v3/search'
    params = {
        'query': query,
        'x_cg_demo_api_key': api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data['coins']:
        return data['coins'][0]['id']
    return None
