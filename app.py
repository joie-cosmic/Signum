from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import os
import concurrent.futures

from services.price import get_coin_data, search_coin
from services.news import get_news
from services.onchain import get_whale_activity, get_exchange_flow, get_stablecoin_flow
from services.ai import analyze
from services.backtest import calculate_backtest

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

    # 先拿币价（其他API需要symbol）
    price_data = get_coin_data(coin_id)
    if not price_data:
        return jsonify({'error': 'Failed to fetch price data'}), 500

    # 并行调用剩余所有API
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_news = executor.submit(get_news, price_data['symbol'])
        future_whale = executor.submit(get_whale_activity, coin_id)
        future_exchange = executor.submit(get_exchange_flow, coin_id)
        future_stablecoin = executor.submit(get_stablecoin_flow)
        future_backtest = executor.submit(calculate_backtest, coin_id)

        news_list = future_news.result()
        whale_data = future_whale.result()
        exchange_flow = future_exchange.result()
        stablecoin_data = future_stablecoin.result()
        backtest_data = future_backtest.result()

    # AI综合分析
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
        'backtest': backtest_data,  # 历史回测数据
        'signal': ai_result
    })

if __name__ == '__main__':
    app.run(debug=True)