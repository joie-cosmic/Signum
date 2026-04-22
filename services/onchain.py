import requests
import os

KNOWN_EXCHANGES = {
    'binance': '0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE',
    'coinbase': '0x71660c4005BA85c37ccec55d0C4493E66Fe775d3',
    'kraken': '0x2910543Af39abA0Cd09dBb2D50200b3E800A63D2',
}

STABLECOIN_CONTRACTS = {
    'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
    'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
}

def get_whale_activity(coin_id: str) -> dict:
    """Get large transactions in the last 24h."""
    api_key = os.getenv('ETHERSCAN_API_KEY')

    url = 'https://api.etherscan.io/v2/api'
    params = {
        'chainid': 1,
        'module': 'account',
        'action': 'txlist',
        'address': KNOWN_EXCHANGES['binance'],
        'startblock': 0,
        'endblock': 99999999,
        'page': 1,
        'offset': 20,
        'sort': 'desc',
        'apikey': api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get('status') != '1':
        return {'net_flow': 0, 'signal': 'neutral', 'large_txns': 0}

    large_txns = 0
    net_flow = 0

    for tx in data.get('result', []):
        value_eth = int(tx.get('value', 0)) / 1e18
        if value_eth > 100:
            large_txns += 1
            if tx['to'].lower() == KNOWN_EXCHANGES['binance'].lower():
                net_flow += value_eth
            else:
                net_flow -= value_eth

    if net_flow > 500:
        signal = 'bearish'
    elif net_flow < -500:
        signal = 'bullish'
    else:
        signal = 'neutral'

    return {
        'net_flow': round(net_flow, 2),
        'signal': signal,
        'large_txns': large_txns
    }

def get_stablecoin_flow() -> dict:
    """Check stablecoin supply as buying power indicator."""
    api_key = os.getenv('ETHERSCAN_API_KEY')

    url = 'https://api.etherscan.io/v2/api'
    params = {
        'chainid': 1,
        'module': 'stats',
        'action': 'tokensupply',
        'contractaddress': STABLECOIN_CONTRACTS['USDT'],
        'apikey': api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get('status') != '1':
        return {'usdt_supply_billions': 0, 'signal': 'neutral'}

    supply = int(data.get('result', 0)) / 1e6

    if supply > 80_000_000_000:
        signal = 'bullish'
    elif supply < 50_000_000_000:
        signal = 'bearish'
    else:
        signal = 'neutral'

    return {
        'usdt_supply_billions': round(supply / 1e9, 2),
        'signal': signal
    }

def get_exchange_flow() -> dict:
    """Get net ETH flow into/out of major exchanges."""
    whale = get_whale_activity('ethereum')

    if whale['net_flow'] > 0:
        signal = 'bearish'
        description = f"{abs(whale['net_flow'])} ETH flowing INTO exchanges — selling pressure"
    elif whale['net_flow'] < 0:
        signal = 'bullish'
        description = f"{abs(whale['net_flow'])} ETH flowing OUT of exchanges — holding signal"
    else:
        signal = 'neutral'
        description = "Exchange flows balanced — no clear signal"

    return {
        'net_flow': whale['net_flow'],
        'signal': signal,
        'description': description,
        'large_txns': whale['large_txns']
    }