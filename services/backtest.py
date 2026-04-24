import requests
import os

def get_historical_prices(coin_id: str, days: int = 30) -> list:
    """Get historical daily prices for a coin."""
    api_key = os.getenv('COINGECKO_API_KEY')
    url = f'https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart'
    params = {
        'vs_currency': 'usd',
        'days': days,
        'interval': 'daily',
        'x_cg_demo_api_key': api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get('prices', [])

def calculate_backtest(coin_id: str) -> dict:
    """
    Calculate historical win rate when bullish signals appear.
    Signal: price goes up next day = win
    We look at 30 days of data and calculate:
    - How many days had positive next-day returns
    - Average gain on up days
    - Average loss on down days
    """
    prices = get_historical_prices(coin_id, days=30)

    if len(prices) < 2:
        return {
            'win_rate': 0,
            'avg_gain': 0,
            'avg_loss': 0,
            'sample_size': 0,
            'summary': 'Insufficient historical data'
        }

    gains = []
    losses = []

    for i in range(len(prices) - 1):
        today_price = prices[i][1]
        tomorrow_price = prices[i + 1][1]
        pct_change = ((tomorrow_price - today_price) / today_price) * 100

        if pct_change > 0:
            gains.append(pct_change)
        else:
            losses.append(pct_change)

    total = len(gains) + len(losses)
    win_rate = round((len(gains) / total) * 100, 1) if total > 0 else 0
    avg_gain = round(sum(gains) / len(gains), 2) if gains else 0
    avg_loss = round(sum(losses) / len(losses), 2) if losses else 0

    summary = (
        f"Over the past 30 days, {coin_id.upper()} closed higher the next day "
        f"{win_rate}% of the time. "
        f"Average gain on up days: +{avg_gain}%. "
        f"Average loss on down days: {avg_loss}%."
    )

    return {
        'win_rate': win_rate,
        'avg_gain': avg_gain,
        'avg_loss': avg_loss,
        'sample_size': total,
        'summary': summary
    }