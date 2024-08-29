import time
import os
from datetime import datetime
from binance.spot import Spot
from binance.error import ClientError
from trading_strategy import TradingStrategy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Determine the environment and configure the Binance client
environment = os.getenv('ENVIRONMENT')
api_key = os.getenv(f'{environment.upper()}_API_KEY')
api_secret = os.getenv(f'{environment.upper()}_API_SECRET')
client = Spot(api_key=api_key, api_secret=api_secret,
              base_url='https://testnet.binance.vision' if environment == 'paper' else 'https://api.binance.com')

# Specific settings for trading
symbol = os.getenv('TRADING_SYMBOL', "BTCUSDT")
timeframe = "15m"
target_profit = 50.0  # In terms of USDT
risk_percent = 1.0  # Risk of 1% of capital per trade
stop_loss_percent = 1.0  # Stop loss of 1% per trade
wait_time = 15 * 60  # Wait time in seconds between trades
trade_fee_rate = 0  # Example of a 0% trading fee
max_usdt_per_trade = 0.2  # Maximum percentage of USDT to use per trade
trailing_stop_percent = 0.02  # 2% below the highest price reached

# Initialize the trading strategy
strategy = TradingStrategy(
    client=client,
    symbol=symbol,
    timeframe=timeframe,
    trade_fee_rate=trade_fee_rate,
    max_usdt_per_trade=max_usdt_per_trade,
    risk_percent=risk_percent,
    stop_loss_percent=stop_loss_percent,
    trailing_stop_percent=trailing_stop_percent
)

def get_initial_balance():
    """Get the initial BTC and USDT balance of the account."""
    #return 0.000017, 150  # Example values for testing
    try:
        account_info = client.account()
        balances = {item['asset']: float(item['free']) for item in account_info['balances']}
        btc_balance = balances.get('BTC', 0)
        usdt_balance = balances.get('USDT', 0)
        return btc_balance, usdt_balance
    except ClientError as e:
        print(f"Error getting the account balance: {e}")
        return 0, 0  # Returns 0 for both balances in case of error

def run_bot():
    global total_profit
    btc_balance, usdt_balance = get_initial_balance()
    print(f"Initial balance: {btc_balance} BTC, {usdt_balance} USDT")

    iteration = 0
    try:
        while strategy.total_profit < target_profit:
            print(f"\nIteration {iteration}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            iteration += 1
            df = strategy.fetch_data()
            df_filtered = strategy.apply_strategies(df)
            latest_signal = df_filtered.iloc[-1]['signal']
            btc_balance, usdt_balance = strategy.execute_trade(latest_signal, btc_balance, usdt_balance)
            time.sleep(wait_time)  # Wait before the next iteration

    except KeyboardInterrupt:
        print("\nBot execution interrupted by user. Exiting safely...")
        # Add any necessary cleanup code before exiting, if needed.

    print(f"Target reached: {strategy.total_profit:.2f} USDT")

if __name__ == "__main__":
    run_bot()
