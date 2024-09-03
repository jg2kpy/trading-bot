import pandas as pd
from binance.spot import Spot
from datetime import datetime

def download_historical_data(symbol, interval, start_str, end_str=None):
    client = Spot(base_url='https://api.binance.com')

    # Convertir fechas a milisegundos
    start_time = int(datetime.strptime(start_str, "%d %b, %Y").timestamp() * 1000)
    end_time = int(datetime.strptime(end_str, "%d %b, %Y").timestamp() * 1000) if end_str else None

    bars = client.klines(symbol=symbol, interval=interval, startTime=start_time, endTime=end_time)

    # Convertir los datos a un DataFrame
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                     'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                     'taker_buy_quote_asset_volume', 'ignore'])

    # Convertir columnas a tipos de datos apropiados
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].apply(pd.to_numeric)

    return df

# Descargar datos históricos para BTCUSDT
df = download_historical_data(symbol='BTCUSDT', interval='30m', start_str='1 Jan, 2023', end_str='28 Aug, 2024')

# Guardar los datos en un archivo CSV
df.to_csv('historical_btcusdt_data.csv', index=False)
print("Datos históricos guardados en 'historical_btcusdt_data.csv'")
