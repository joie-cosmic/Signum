# Signum — Onchain Intelligence

> The market moves before the news breaks.

Signum is a crypto market signal platform that combines real-time onchain data, news analysis, and AI to help users understand what the market is actually doing.

## Live Demo

https://signum-liart.vercel.app/

## What Signum Does

Users search any cryptocurrency and receive a comprehensive signal analysis backed by:

- **Whale wallet tracking** — Real onchain large transactions (>100 ETH/BTC/SOL)
- **Exchange fund flows** — Net capital moving into/out of major exchanges
- **Stablecoin supply** — USDT/USDC on-chain liquidity as buying power indicator
- **News analysis** — Weighted crypto news with AI interpretation
- **Historical backtest** — 30-day win rate and average gain/loss data
- **AI signal** — Claude synthesizes all data into BULLISH/NEUTRAL/BEARISH with reasoning

## Web3 Component

Signum's web3 component is real and central to the product:

- **Etherscan V2 API** — Tracks whale transactions on Ethereum mainnet (chainid=1) and BNB Chain (chainid=56)
- **Mempool.space API** — Tracks large BTC transactions in real-time
- **Solana RPC** — Monitors Solana wallet activity
- **XRPL API** — Tracks XRP ledger transactions
- **Stablecoin contract monitoring** — Reads USDT supply directly from the smart contract on Ethereum

## Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **Price Data:** CoinGecko API
- **News Data:** NewsData.io API
- **Onchain Data:** Etherscan V2, Mempool.space, Solana RPC, XRPL
- **AI Analysis:** Claude API (Anthropic)
- **Deployment:** Vercel

## Setup Instructions

### 1. Clone the repo
\`\`\`bash
git clone https://github.com/joie-cosmic/Signum
cd Signum
\`\`\`

### 2. Create virtual environment
\`\`\`bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

### 3. Set up environment variables
Create a \`.env\` file:
\`\`\`
COINGECKO_API_KEY=your_key
NEWSDATA_API_KEY=your_key
ETHERSCAN_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
\`\`\`

### 4. Run locally
\`\`\`bash
python3 app.py
\`\`\`

Visit \`http://127.0.0.1:5000\`

## How It Works

User searches a coin → Parallel API calls (price, news, onchain data, backtest) → Claude AI synthesizes → BULLISH/NEUTRAL/BEARISH signal with reasoning

## Supported Chains

| Chain | Data Source |
|-------|------------|
| Ethereum | Etherscan V2 |
| BNB Chain | Etherscan V2 (chainid=56) |
| Bitcoin | Mempool.space |
| Solana | Solana RPC |
| XRP | XRPL Cluster |
