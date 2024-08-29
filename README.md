
# Automated BTC Trading Bot

This is a simple, open-source automated trading bot for Bitcoin (BTC), created as a project by a Computer Science major. The bot is designed to execute trades on the Binance exchange based on various technical analysis indicators. The project is licensed under the MIT License.

## Features

- Connects to Binance API for live trading or paper trading (testnet).
- Implements a configurable trading strategy using indicators such as SMA, RSI, MACD, and Bollinger Bands.
- Manages trades with risk control measures like stop-loss and trailing stop.
- Logs and displays trade execution details and profit tracking.

## Installation

### Prerequisites

- Python 3.8 or higher
- Binance account (for live trading)

### Step-by-step installation

#### Windows

1. Download and install Python from the official [Python website](https://www.python.org/downloads/).
2. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/trading-bot.git
    cd trading-bot
    ```
3. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

#### macOS

1. Install Python using Homebrew:
    ```bash
    brew install python
    ```
2. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/trading-bot.git
    cd trading-bot
    ```
3. Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
4. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

#### Linux (Debian/Ubuntu)

1. Install Python:
    ```bash
    sudo apt update
    sudo apt install python3 python3-venv python3-pip
    ```
2. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/trading-bot.git
    cd trading-bot
    ```
3. Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
4. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

### .env File Setup

The bot requires a `.env` file for configuration, which includes API keys and trading settings. Here is an example of how to set up your `.env` file:

```ini
# Environment setting
ENVIRONMENT=paper

# Live environment API keys
LIVE_API_KEY=your_binance_api_key
LIVE_API_SECRET=your_binance_api_secret

# Paper environment API keys
PAPER_API_KEY=your_testnet_api_key
PAPER_API_SECRET=your_testnet_api_secret

# Trading symbol
TRADING_SYMBOL=BTCUSDT
```

- **ENVIRONMENT**: Set this to `paper` for testnet (paper trading) or `live` for real trading.
- **LIVE_API_KEY / LIVE_API_SECRET**: Your Binance API key and secret for live trading.
- **PAPER_API_KEY / PAPER_API_SECRET**: Your Binance API key and secret for paper trading (testnet).
- **TRADING_SYMBOL**: The trading pair symbol, e.g., `BTCUSDT`.

### Setting Up Your Environment

1. Rename `.env.example` to `.env`.
2. Replace `your_binance_api_key` and `your_binance_api_secret` with your actual Binance API credentials.

## Running the Bot

To start the trading bot, simply run the following command:

```bash
cd src/
python main.py
```

The bot will begin fetching market data, applying the trading strategy, and executing trades based on the signals generated.

## Feedback and Contributions

This is an open-source project, and contributions are welcome! Please open issues or pull requests with any suggestions or improvements.

### Feedback on Trading Strategy

The current trading strategy uses a combination of Simple Moving Averages (SMA), Relative Strength Index (RSI), Moving Average Convergence Divergence (MACD), and Bollinger Bands. We are particularly interested in feedback on the following:

1. **Risk Management**: Are there better ways to implement risk management to avoid significant losses?
2. **Technical Indicators**: Are there more effective indicators or configurations to improve trade accuracy?
3. **Optimization**: How can we optimize the execution of trades to reduce slippage and fees?

Feel free to reach out via GitHub issues or contribute directly through pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
