import anthropic
import os

def analyze(coin_name: str, coin_symbol: str, price_data: dict,
            news_list: list, whale_data: dict,
            exchange_flow: dict, stablecoin_data: dict) -> dict:
    """Use Claude to analyze all data and generate a signal."""

    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    news_text = '\n'.join([
        f"[{n['weight'].upper()}] {n['title']}"
        for n in news_list[:5]
    ])

    prompt = f"""You are a crypto market analyst. Analyze the following data for {coin_name} ({coin_symbol}) and provide a signal.

CURRENT PRICE DATA:
- Price: ${price_data['price']:,.2f}
- 24h Change: {price_data['change_24h']:.2f}%
- 24h Volume: ${price_data['volume_24h']:,.0f}

ONCHAIN DATA (this is real blockchain data):
- Whale Activity: {whale_data['large_txns']} large transactions (>100 ETH)
- Exchange Net Flow: {exchange_flow['net_flow']} ETH ({exchange_flow['signal']})
- Exchange Description: {exchange_flow['description']}
- USDT Supply on Chain: ${stablecoin_data['usdt_supply_billions']:.1f}B ({stablecoin_data['signal']})

RECENT NEWS (sorted by importance):
{news_text}

Based on ALL of the above data, provide your analysis in this EXACT format:

SIGNAL: [BULLISH/BEARISH/NEUTRAL]

ONCHAIN_SUMMARY: [2-3 sentences explaining what the onchain data shows. Must include specific numbers. Must reference historical patterns if applicable.]

NEWS_SUMMARY: [2-3 sentences explaining the most important news and its likely impact.]

REASONING: [3-4 sentences combining onchain + news into a final conclusion. Be specific, not vague. Never say 'exercise caution' without explaining why.]

CONFIDENCE: [HIGH/MEDIUM/LOW]

Remember: You must give a specific, data-backed explanation. Vague responses like 'market is uncertain' are not acceptable."""

    message = client.messages.create(
        model='claude-sonnet-4-5',
        max_tokens=1000,
        messages=[{'role': 'user', 'content': prompt}]
    )

    response_text = message.content[0].text

    lines = response_text.strip().split('\n')
    result = {
        'signal': 'NEUTRAL',
        'onchain_summary': '',
        'news_summary': '',
        'reasoning': '',
        'confidence': 'MEDIUM'
    }

    current_key = None
    current_value = []

    for line in lines:
        if line.startswith('SIGNAL:'):
            result['signal'] = line.replace('SIGNAL:', '').strip()
        elif line.startswith('ONCHAIN_SUMMARY:'):
            current_key = 'onchain_summary'
            current_value = [line.replace('ONCHAIN_SUMMARY:', '').strip()]
        elif line.startswith('NEWS_SUMMARY:'):
            if current_key:
                result[current_key] = ' '.join(current_value).strip()
            current_key = 'news_summary'
            current_value = [line.replace('NEWS_SUMMARY:', '').strip()]
        elif line.startswith('REASONING:'):
            if current_key:
                result[current_key] = ' '.join(current_value).strip()
            current_key = 'reasoning'
            current_value = [line.replace('REASONING:', '').strip()]
        elif line.startswith('CONFIDENCE:'):
            if current_key:
                result[current_key] = ' '.join(current_value).strip()
            result['confidence'] = line.replace('CONFIDENCE:', '').strip()
            current_key = None
        elif current_key and line.strip():
            current_value.append(line.strip())

    return result
