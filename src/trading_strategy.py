import pandas as pd
import talib
from binance.spot import Spot
from binance.error import ClientError
from utils import get_symbol_info, get_lot_size_info, adjust_quantity, calculate_trade_amount

class TradingStrategy:
    def __init__(self, client, symbol, timeframe, trade_fee_rate, max_usdt_per_trade, risk_percent, stop_loss_percent, trailing_stop_percent):
        self.client = client
        self.symbol = symbol
        self.timeframe = timeframe
        self.trade_fee_rate = trade_fee_rate
        self.max_usdt_per_trade = max_usdt_per_trade
        self.risk_percent = risk_percent
        self.stop_loss_percent = stop_loss_percent
        self.trailing_stop_percent = trailing_stop_percent
        self.trailing_stop_price = None
        self.last_buy_price = None
        self.total_profit = 0

    def fetch_data(self):
        """Fetch market data"""
        bars = self.client.klines(self.symbol, interval=self.timeframe)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].apply(pd.to_numeric)
        return df

    def apply_strategies(self, df):
        """Apply trading strategies with adjusted parameters"""
        # Adjust volatility calculation
        df['volatility'] = df['high'] - df['low']
        volatility_threshold = df['volatility'].quantile(0.95)
        df_filtered = df[df['volatility'] < volatility_threshold].copy()

        # Adjust SMAs
        df_filtered['SMA_short'] = talib.SMA(df_filtered['close'], timeperiod=10)
        df_filtered['SMA_long'] = talib.SMA(df_filtered['close'], timeperiod=20)

        # Adjust RSI
        df_filtered['RSI'] = talib.RSI(df_filtered['close'], timeperiod=14)

        # Adjust MACD
        df_filtered['MACD'], df_filtered['MACD_signal'], _ = talib.MACD(df_filtered['close'], fastperiod=5, slowperiod=35, signalperiod=5)

        # Adjust Bollinger Bands
        df_filtered['upper_band'], df_filtered['middle_band'], df_filtered['lower_band'] = talib.BBANDS(df_filtered['close'], timeperiod=20, nbdevup=2.5, nbdevdn=2.5, matype=0)

        # Trading signals based on adjusted strategies
        df_filtered['signal'] = 0
        df_filtered.loc[(df_filtered['SMA_short'] > df_filtered['SMA_long']) & (df_filtered['RSI'] < 70) & (df_filtered['MACD'] > df_filtered['MACD_signal']), 'signal'] = 1
        df_filtered.loc[(df_filtered['SMA_short'] < df_filtered['SMA_long']) & (df_filtered['RSI'] > 30) & (df_filtered['MACD'] < df_filtered['MACD_signal']), 'signal'] = -1
        df_filtered.loc[df_filtered['close'] > df_filtered['upper_band'], 'signal'] = -1
        df_filtered.loc[df_filtered['close'] < df_filtered['lower_band'], 'signal'] = 1

        return df_filtered

    def execute_trade(self, signal, btc_balance, usdt_balance):
        """Execute a trade based on the signal with risk control"""
        print(f"Executing trade with signal: {signal}, BTC balance: {round(btc_balance, 8)}, USDT balance: {usdt_balance:.2f}")
        symbol_info = get_symbol_info(self.client, self.symbol)
        if symbol_info is None:
            print(f"Error: could not obtain information for symbol {self.symbol}.")
            return btc_balance, usdt_balance

        min_qty, step_size, min_notional = get_lot_size_info(symbol_info)

        if signal == 1:
            return self.handle_buy(btc_balance, usdt_balance, min_qty, step_size, min_notional)

        elif signal == -1:
            return self.handle_sell(btc_balance, usdt_balance, min_qty, step_size, min_notional)

        return btc_balance, usdt_balance

    def handle_buy(self, btc_balance, usdt_balance, min_qty, step_size, min_notional):
        """Handle buy logic"""
        trade_amount = calculate_trade_amount(usdt_balance, self.risk_percent, self.stop_loss_percent)
        max_trade_amount = usdt_balance * self.max_usdt_per_trade

        ticker = self.client.ticker_price(symbol=self.symbol)
        current_price = float(ticker['price'])
        quantity = min(trade_amount / current_price, max_trade_amount / current_price)
        quantity = adjust_quantity(quantity, step_size)

        total_cost = quantity * current_price * (1 + self.trade_fee_rate)

        if quantity < min_qty or total_cost < min_notional:
            print("Adjusting quantity to meet minimum quantity and notional value requirements.")
            quantity = max(min_qty, (min_notional + 1) / current_price)
            quantity = adjust_quantity(quantity, step_size)
            total_cost = quantity * current_price * (1 + self.trade_fee_rate)

        print(f"Attempting to buy {quantity} BTC at a price of {current_price} USDT/BTC. Estimated total cost: {total_cost:.2f} USDT.")

        if usdt_balance >= total_cost:
            order = self.client.new_order(symbol=self.symbol, side="BUY", type="MARKET", quantity="{:.8f}".format(quantity))
            self.last_buy_price = float(order['fills'][0]['price'])
            self.trailing_stop_price = self.last_buy_price * (1 - self.trailing_stop_percent)
            print(f"Successful purchase: {quantity} BTC at a price of {self.last_buy_price} USDT/BTC. Total cost: {total_cost:.2f} USDT.")
            btc_balance += quantity
            usdt_balance -= total_cost
        else:
            print("Insufficient funds: not enough USDT to complete the purchase.")

        return btc_balance, usdt_balance

    def handle_sell(self, btc_balance, usdt_balance, min_qty, step_size, min_notional):
        """Handle sell logic"""
        if btc_balance < min_qty:
            print(f"The BTC balance ({btc_balance:.8f} BTC) is less than the required minimum ({min_qty} BTC) to perform a sale.")
            print("No sale will be made in this iteration due to insufficient balance.")
            return btc_balance, usdt_balance

        current_price = float(self.client.ticker_price(symbol=self.symbol)['price'])

        # Check if a previous buy price has been set
        if self.last_buy_price is None:
            print("Cannot sell because no previous purchase has been made.")
            return btc_balance, usdt_balance

        if current_price > self.last_buy_price:
            self.trailing_stop_price = current_price * (1 - self.trailing_stop_percent)
            self.last_buy_price = current_price
            print(f"New maximum price reached: {self.last_buy_price} USDT/BTC, trailing stop updated to {self.trailing_stop_price:.2f} USDT/BTC.")

        if current_price > self.trailing_stop_price:
            print(f"The current price ({current_price} USDT/BTC) has not reached the trailing stop ({self.trailing_stop_price} USDT/BTC). No sale will be made in this iteration.")
            return btc_balance, usdt_balance

        print(f"The current price ({current_price} USDT/BTC) has reached the trailing stop ({self.trailing_stop_price} USDT/BTC). Considering selling.")
        distance_to_stop = self.last_buy_price - current_price
        quantity_to_sell = btc_balance * (distance_to_stop / self.last_buy_price)
        quantity = adjust_quantity(quantity_to_sell, step_size)

        print(f"Attempting to sell {quantity:.8f} BTC to secure profits based on the price drop.")

        total_sale = quantity * current_price * (1 - self.trade_fee_rate)

        if total_sale < min_notional:
            print(f"The estimated total sale ({total_sale:.2f} USDT) is less than the allowed minimum notional value ({min_notional} USDT). Adjusting sale quantity.")
            quantity = adjust_quantity((min_notional + 1) / current_price, step_size)
            total_sale = quantity * current_price * (1 - self.trade_fee_rate)

        if total_sale < min_notional:
            print(f"Sale not executed because the adjusted total sale ({total_sale:.2f} USDT) is still less than the allowed minimum notional value ({min_notional} USDT).")
            return btc_balance, usdt_balance

        try:
            order = self.client.new_order(symbol=self.symbol, side="SELL", type="MARKET", quantity="{:.8f}".format(quantity))
            sell_price = float(order['fills'][0]['price'])
            profit = (sell_price - self.last_buy_price) * quantity
            self.total_profit += profit
            usdt_balance += total_sale
            btc_balance -= quantity
            print(f"Successful sale: {quantity:.8f} BTC sold at a price of {sell_price} USDT/BTC. Total received: {total_sale:.2f} USDT.")
            print(f"Profit from this trade: {profit:.2f} USDT. Total accumulated profit: {self.total_profit:.2f} USDT.")
        except ClientError as e:
            print(f"Error attempting to sell: {e}")

        return btc_balance, usdt_balance
