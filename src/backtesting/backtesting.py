import pandas as pd
from trading_strategy import TradingStrategy
from binance.spot import Spot
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()

# Inicializar cliente de Binance (puedes usar las claves para testnet para evitar operaciones reales)
environment = os.getenv('ENVIRONMENT')
api_key = os.getenv(f'{environment.upper()}_API_KEY')
api_secret = os.getenv(f'{environment.upper()}_API_SECRET')
client = Spot(api_key=api_key, api_secret=api_secret,
              base_url='https://testnet.binance.vision' if environment == 'paper' else 'https://api.binance.com')

# Configuración específica para el backtesting
symbol = os.getenv('TRADING_SYMBOL', "BTCUSDT")
timeframe = "15m"
trade_fee_rate = 0.001  # Ejemplo de una tasa de 0.1%
max_usdt_per_trade = 0.2  # Usar un máximo de 20% de USDT por trade
risk_percent = 1.0  # Riesgo de 1% del capital por trade
stop_loss_percent = 1.0  # Stop loss de 1% por trade
trailing_stop_percent = 0  # Trailing stop de 2% por debajo del máximo alcanzado

# Inicializar la estrategia de trading
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

# Leer datos históricos
historical_data = pd.read_csv('historical_btcusdt_data.csv')  # Asegúrate de que este archivo exista y esté bien formateado

# Saldos iniciales para la simulación
initial_btc_balance = 0.000017  # Ejemplo de saldo inicial de BTC
initial_usdt_balance = 150  # Ejemplo de saldo inicial de USDT

# Ejecutar el backtesting
total_profit = strategy.run_backtesting(historical_data, initial_btc_balance, initial_usdt_balance)
print(f"Backtesting completed. Total profit: {total_profit:.2f} USDT")
