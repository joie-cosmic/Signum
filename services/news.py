import requests
import os

WEIGHT_MAP = {
    'high': ['regulation', 'sec', 'government', 'ban', 'legal', 'blackrock',
             'fidelity', 'etf', 'federal reserve', 'fed', 'institution'],
    'medium': ['upgrade', 'partnership', 'launch', 'protocol', 'inflation',
               'interest rate', 'gdp', 'economy'],
}


def get_weight(title: str) -> str:
    """Assign weight to news based on keywords in title."""
    title_lower = title.lower()
    for keyword in WEIGHT_MAP['high']:
        if keyword in title_lower:
            return 'high'
    for keyword in WEIGHT_MAP['medium']:
        if keyword in title_lower:
            return 'medium'
    return 'low'


def get_news(coin_symbol: str) -> list:
    """Fetch latest news for a coin."""
    api_key = os.getenv('NEWSDATA_API_KEY')

    url = 'https://newsdata.io/api/1/news'
    params = {
        'apikey': api_key,
        'q': f'{coin_symbol} crypto',
        'language': 'en',
        'category': 'business,technology',
        'size': 5
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get('status') != 'success':
        return []

    news_list = []
    for article in data.get('results', []):
        if not article.get('title'):
            continue
        news_list.append({
            'title': article['title'],
            'description': article.get('description', ''),
            'url': article.get('link', ''),
            'published': article.get('pubDate', ''),
            'weight': get_weight(article['title'])
        })

    news_list.sort(key=lambda x: {'high': 0, 'medium': 1, 'low': 2}[x['weight']])

    return news_list
