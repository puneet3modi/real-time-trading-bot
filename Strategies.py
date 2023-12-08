import numpy as np 
import json
from collections import deque

class CrossOverMA:
    def __init__(self, fraction=0.1):
        self.window_50 = deque(maxlen=50)
        self.window_20 = deque(maxlen=20)
        self.fraction = fraction
        self.signal = None # True for buy, False for sell
    
    def CheckForSignalShift(self):
        if len(self.window_50) < 50 or len(self.window_20) < 20:
            return False  # Return False if the windows are not fully populated
        current_signal = np.average(self.window_50) < np.average(self.window_20)
        if self.signal is None:
            self.signal = current_signal
            return False  # No signal change can be detected on the first run
        new_signal = current_signal != self.signal
        self.signal = current_signal  # Update the signal for next call
        return new_signal
    
    def ProcessMarketDataAndGenerateOrder(self, received, current_capital):
        received = json.loads(received.replace("'", '"'))
        price = float(received['Close'])
        current_holdings = float(received['Holdings'])
        self.window_20.append(price)
        self.window_50.append(price)
        if self.CheckForSignalShift():
            print('MOVING AVERAGE SIGNAL CHANGED')
            if not self.signal:  # MA50 > MA20, indicating a sell signal
                order = {'Direction': 'Sell', 'Amount': current_holdings}
            else:  # MA50 < MA20, indicating a buy signal
                order = {'Direction': 'Buy', 'Amount': self.fraction * current_capital / price}
        else:
            order = None
        return order
    
class Momentum:
    def __init__(self, fraction=0.1, lookback_period=50, buy_threshold=0.05, sell_threshold=-0.05):
        self.prices = deque(maxlen=lookback_period)
        self.fraction = fraction
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    def ProcessMarketDataAndGenerateOrder(self, received, current_capital):
        received = json.loads(received.replace("'", '"'))
        price = float(received['Close'])
        current_holdings = float(received['Holdings'])
        self.prices.append(price)
        if len(self.prices) < self.prices.maxlen:
            return None
        recent_price = self.prices[-1]
        past_price = self.prices[0]
        price_change = (recent_price - past_price) / past_price
        if price_change >= self.buy_threshold:
            print('MOMENTUM BUY SIGNAL')
            order = {'Direction': 'Buy', 'Amount': self.fraction * current_capital / price}
        elif price_change <= self.sell_threshold:
            print('MOMENTUM SELL SIGNAL')
            order = {'Direction': 'Sell', 'Amount': current_holdings}
        else:
            order = None
        return order

# class RSI:
#     def __init__(self, period=14, upper_threshold=70, lower_threshold=30, fraction=0.1):
#         self.price_changes = deque(maxlen=period)
#         self.fraction = fraction
#         self.upper_threshold = upper_threshold
#         self.lower_threshold = lower_threshold

#     def ComputeRelativeStrengthIndex(self):
#         gains = sum([change for change in self.price_changes if change > 0])
#         losses = sum([-change for change in self.price_changes if change < 0])
#         if losses == 0:
#             return 100
#         average_gain = gains / len(self.price_changes)
#         average_loss = losses / len(self.price_changes)
#         rs = average_gain / average_loss
#         return 100 - (100 / (1 + rs))
    
#     def ProcessMarketDataAndGenerateOrder(self, received, current_capital):
#         received = json.loads(received.replace("'", '"'))
#         price = float(received['Close'])
#         current_holdings = float(received['Holdings'])
#         if self.price_changes:
#             price_change = price - self.price_changes[-1]
#         else:
#             price_change = 0
#         self.price_changes.append(price_change)
#         if len(self.price_changes) < self.price_changes.maxlen:
#             return None
#         rsi = self.ComputeRelativeStrengthIndex()
#         if rsi < self.lower_threshold:
#             print('RSI BUY SIGNAL')
#             order = {'Direction': 'Buy', 'Amount': self.fraction * current_capital / price}
#         elif rsi > self.upper_threshold:
#             print('RSI SELL SIGNAL')
#             order = {'Direction': 'Sell', 'Amount': current_holdings}
#         else:
#             order = None
#         return order

class BollingerBands:
    def __init__(self, period=20, std_dev_multiplier=2, fraction=0.1):
        self.period = period
        self.std_dev_multiplier = std_dev_multiplier
        self.fraction = fraction
        self.prices = deque(maxlen=period)

    def ComputeSimpleMovingAverage(self):
        return np.mean(self.prices)

    def ComputePriceStandardDeviation(self):
        return np.std(self.prices)

    def ProcessMarketDataAndGenerateOrder(self, received, current_capital):
        received = json.loads(received.replace("'", '"'))
        price = float(received['Close'])
        current_holdings = float(received['Holdings'])
        self.prices.append(price)
        if len(self.prices) < self.period:
            return None
        sma = self.ComputeSimpleMovingAverage()
        std_dev = self.ComputePriceStandardDeviation()
        upper_band = sma + (self.std_dev_multiplier * std_dev)
        lower_band = sma - (self.std_dev_multiplier * std_dev)
        if price > upper_band:
            print('BOLLINGER BANDS SELL SIGNAL')
            return {'Direction': 'Sell', 'Amount': current_holdings}
        elif price < lower_band:
            print('BOLLINGER BANDS BUY SIGNAL')
            return {'Direction': 'Buy', 'Amount': self.fraction * current_capital / price}
        else:
            return None

class MeanReversionStrategy:
    def __init__(self, window_size=20, std_dev_factor=2, fraction=0.1):
        self.window_size = window_size
        self.std_dev_factor = std_dev_factor
        self.fraction = fraction
        self.prices = deque(maxlen=window_size)

    def ProcessMarketDataAndGenerateOrder(self, received, current_capital):
        received = json.loads(received.replace("'", '"'))
        price = float(received['Close'])
        current_holdings = float(received['Holdings'])
        self.prices.append(price)
        if len(self.prices) < self.window_size:
            return None  # Not enough data to calculate mean and std deviation
        avg_price = np.mean(self.prices)
        std_dev = np.std(self.prices)
        upper_band = avg_price + self.std_dev_factor * std_dev
        lower_band = avg_price - self.std_dev_factor * std_dev
        if price <= lower_band:
            print('MEAN REVERSION BUY SIGNAL')
            return {'Direction': 'Buy', 'Amount': self.fraction * current_capital / price}
        elif price >= upper_band:
            print('MEAN REVERSION SELL SIGNAL')
            return {'Direction': 'Sell', 'Amount': current_holdings}
        else:
            return None

class MACDStrategy:
    def __init__(self, short_window=12, long_window=26, signal_window=9, fraction=0.1):
        self.short_window = short_window
        self.long_window = long_window
        self.signal_window = signal_window
        self.fraction = fraction
        self.short_ema = deque(maxlen=short_window)
        self.long_ema = deque(maxlen=long_window)
        self.signal_line = deque(maxlen=signal_window)
        self.macd_line = []

    def ComputeExponentialMovingAverage(self, prices, window):
        return prices[-1] * (2 / (window + 1)) + np.mean(prices) * (1 - (2 / (window + 1)))

    def UpdateEMAAndCalculateMACD(self, price):
        self.short_ema.append(price)
        self.long_ema.append(price)
        if len(self.short_ema) == self.short_window and len(self.long_ema) == self.long_window:
            short_ema_val = self.ComputeExponentialMovingAverage(self.short_ema, self.short_window)
            long_ema_val = self.ComputeExponentialMovingAverage(self.long_ema, self.long_window)
            self.macd_line.append(short_ema_val - long_ema_val)
            if len(self.macd_line) > self.signal_window:
                self.signal_line.append(np.mean(self.macd_line[-self.signal_window:]))

    def ProcessMarketDataAndGenerateOrder(self, received, current_capital):
        received = json.loads(received.replace("'", '"'))
        price = float(received['Close'])
        current_holdings = float(received['Holdings'])
        self.UpdateEMAAndCalculateMACD(price)
        if len(self.signal_line) < self.signal_window:
            return None
        macd_val = self.macd_line[-1]
        signal_val = self.signal_line[-1]
        if macd_val > signal_val:
            print('MACD Buy Signal')
            return {'Direction': 'Buy', 'Amount': self.fraction * current_capital / price}
        elif macd_val < signal_val:
            print('MACD Sell Signal')
            return {'Direction': 'Sell', 'Amount': current_holdings}
        else:
            return None
        