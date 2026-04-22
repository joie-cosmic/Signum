from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import os

from services.price import get_coin_data, search_coin
from services.news import get_news
from services.onchain import get_whale_activity, get_exchange_flow, get_stablecoin_flow
from services.ai import analyze

load_dotenv()

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/analyze', methods=['GET'])
def analyze_coin():
    query = request.args.get('coin', 'ethereum')

    # 搜索币种ID
    coin_id = search_coin(query)
    if not coin_id:
        return jsonify({'error': f'Coin "{query}" not found'}), 404

    # 拿所有数据
    price_data = get_coin_data(coin_id)
    if not price_data:
        return jsonify({'error': 'Failed to fetch price data'}), 500

    news_list = get_news(price_data['symbol'])
    whale_data = get_whale_activity(coin_id)
    exchange_flow = get_exchange_flow()
    stablecoin_data = get_stablecoin_flow()

    # AI分析
    ai_result = analyze(
        coin_name=price_data['name'],
        coin_symbol=price_data['symbol'],
        price_data=price_data,
        news_list=news_list,
        whale_data=whale_data,
        exchange_flow=exchange_flow,
        stablecoin_data=stablecoin_data
    )

    return jsonify({
        'price': price_data,
        'news': news_list,
        'onchain': {
            'whale': whale_data,
            'exchange_flow': exchange_flow,
            'stablecoin': stablecoin_data
        },
        'signal': ai_result
    })


if __name__ == '__main__':
    app.run(debug=True)
