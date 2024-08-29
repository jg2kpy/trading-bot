from binance.error import ClientError

def get_symbol_info(client, symbol):
    """Get symbol information for lot size restrictions"""
    try:
        exchange_info = client.exchange_info()
        for s in exchange_info['symbols']:
            if s['symbol'] == symbol:
                return s
        raise ValueError(f"Symbol {symbol} not found in exchange information.")
    except ClientError as e:
        print(f"Error obtaining symbol information: {e}")
        return None

def get_lot_size_info(symbol_info):
    """Get LOT_SIZE and NOTIONAL details for the symbol"""
    if symbol_info is None:
        raise ValueError("Symbol information is None. Cannot proceed with trading.")

    min_qty, step_size, min_notional = None, None, None
    for f in symbol_info['filters']:
        if f['filterType'] == 'LOT_SIZE':
            min_qty = float(f['minQty'])
            step_size = float(f['stepSize'])
        elif f['filterType'] == 'NOTIONAL':
            min_notional = float(f['minNotional'])

    if min_qty is None or step_size is None or min_notional is None:
        raise ValueError("Required symbol info (LOT_SIZE, NOTIONAL) not found for the symbol")

    return min_qty, step_size, min_notional

def adjust_quantity(quantity, step_size):
    """Adjust the quantity to the allowed step size"""
    return round(quantity - (quantity % step_size), 8)

def calculate_trade_amount(usdt_balance, risk_percent, stop_loss_percent):
    """Calculate trade size based on capital and risk"""
    risk_amount = usdt_balance * risk_percent / 100
    trade_amount = risk_amount / (stop_loss_percent / 100)
    return trade_amount
