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

BNB_EXCHANGES = {
    'binance': '0x8894E0a0c962CB723c1976a4421c95949bE2D4E3',
}

CHAIN_MAP = {
    'ethereum': 'eth',
    'bitcoin': 'btc',
    'solana': 'sol',
    'binancecoin': 'bnb',
    'ripple': 'xrp',
}

def get_eth_whale_activity() -> dict:
    """Get large ETH transactions from Etherscan V2."""
    api_key = os.getenv('ETHERSCAN_API_KEY')
    url = 'https://api.etherscan.io/v2/api'
    params = {
        'chainid': 1,
        'module': 'account',
        'action': 'txlist',
        'address': KNOWN_EXCHANGES['binance'],
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

    signal = 'bearish' if net_flow > 500 else 'bullish' if net_flow < -500 else 'neutral'
    return {'net_flow': round(net_flow, 2), 'signal': signal, 'large_txns': large_txns}

def get_bnb_whale_activity() -> dict:
    """Get large BNB transactions from Etherscan V2 BSC."""
    api_key = os.getenv('ETHERSCAN_API_KEY')
    url = 'https://api.etherscan.io/v2/api'
    params = {
        'chainid': 56,
        'module': 'account',
        'action': 'txlist',
        'address': BNB_EXCHANGES['binance'],
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
        value_bnb = int(tx.get('value', 0)) / 1e18
        if value_bnb > 100:
            large_txns += 1
            if tx['to'].lower() == BNB_EXCHANGES['binance'].lower():
                net_flow += value_bnb
            else:
                net_flow -= value_bnb

    signal = 'bearish' if net_flow > 500 else 'bullish' if net_flow < -500 else 'neutral'
    return {'net_flow': round(net_flow, 2), 'signal': signal, 'large_txns': large_txns}

def get_btc_whale_activity() -> dict:
    """Get large BTC transactions from mempool.space."""
    try:
        url = 'https://mempool.space/api/mempool/recent'
        response = requests.get(url, timeout=10)
        txs = response.json()

        large_txns = 0
        net_flow = 0
        for tx in txs:
            value_btc = tx.get('value', 0) / 1e8
            if value_btc > 1:
                large_txns += 1
                net_flow += value_btc

        signal = 'bullish' if large_txns > 5 else 'neutral'
        return {
            'net_flow': round(net_flow, 2),
            'signal': signal,
            'large_txns': large_txns
        }
    except:
        return {'net_flow': 0, 'signal': 'neutral', 'large_txns': 0}

def get_sol_whale_activity() -> dict:
    """Get large SOL transactions from Solana RPC."""
    try:
        url = 'https://api.mainnet-beta.solana.com'
        payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'getRecentBlockhash',
            'params': []
        }
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()

        if data.get('result'):
            return {'net_flow': 0, 'signal': 'neutral', 'large_txns': 0, 'note': 'SOL chain active'}
        return {'net_flow': 0, 'signal': 'neutral', 'large_txns': 0}
    except:
        return {'net_flow': 0, 'signal': 'neutral', 'large_txns': 0}

def get_xrp_whale_activity() -> dict:
    """Get large XRP transactions from XRPL."""
    try:
        url = 'https://xrplcluster.com'
        payload = {
            'method': 'server_info',
            'params': [{}]
        }
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()

        if data.get('result'):
            return {'net_flow': 0, 'signal': 'neutral', 'large_txns': 0, 'note': 'XRP chain active'}
        return {'net_flow': 0, 'signal': 'neutral', 'large_txns': 0}
    except:
        return {'net_flow': 0, 'signal': 'neutral', 'large_txns': 0}

def get_whale_activity(coin_id: str) -> dict:
    """Route to correct chain based on coin_id."""
    chain = CHAIN_MAP.get(coin_id, 'eth')

    if chain == 'btc':
        return get_btc_whale_activity()
    elif chain == 'bnb':
        return get_bnb_whale_activity()
    elif chain == 'sol':
        return get_sol_whale_activity()
    elif chain == 'xrp':
        return get_xrp_whale_activity()
    else:
        return get_eth_whale_activity()

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
    signal = 'bullish' if supply > 80_000_000_000 else 'bearish' if supply < 50_000_000_000 else 'neutral'

    return {
        'usdt_supply_billions': round(supply / 1e9, 2),
        'signal': signal
    }

def get_exchange_flow(coin_id: str = 'ethereum') -> dict:
    """Get net flow into/out of exchanges for given coin."""
    whale = get_whale_activity(coin_id)

    if whale['net_flow'] > 0:
        signal = 'bearish'
        description = f"{abs(whale['net_flow'])} flowing INTO exchanges — selling pressure"
    elif whale['net_flow'] < 0:
        signal = 'bullish'
        description = f"{abs(whale['net_flow'])} flowing OUT of exchanges — holding signal"
    else:
        signal = 'neutral'
        description = "Exchange flows balanced — no clear signal"

    return {
        'net_flow': whale['net_flow'],
        'signal': signal,
        'description': description,
        'large_txns': whale['large_txns']
    }
