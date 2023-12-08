import socket
import json
# import sys
# from collections import deque
# from threading import Thread
from Strategies import CrossOverMA, Momentum, BollingerBands, MeanReversionStrategy, MACDStrategy
import logging

logging.basicConfig(filename='client.log', 
                    level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class Client:
    def __init__(self, HOST="localhost", PORT=9999, init_capital=1e6, strat=None):
        logging.debug("Initializing trading client")
        self.HOST = HOST
        self.PORT = PORT
        self.capital = init_capital
        self.getStrategy(strat)
        self.price = None  # Add a price attribute to store the latest price

    def getStrategy(self, strat):
        logging.debug(f"Setting strategy: {strat.__name__}")
        self.strat = strat
    
    def _connect(self):
        logging.info(f"Attempting to connect to server at {self.HOST}:{self.PORT}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.sock:
            self.sock.connect((self.HOST, self.PORT))
            while True:
                try:
                    received = str(self.sock.recv(1024), "utf-8")
                    logging.info(f"Received data: {received}")
                    print("Received: {}".format(received))
                    if not received.strip():
                        logging.warning("No data received, continuing")
                        print("No data received")
                        continue
                    rcvd_json = json.loads(received.replace("'", '"'))
                    self.price = float(rcvd_json['Close'])  # Update the price attribute
                    order = self.strat(received=received, current_capital=self.capital)
                    cash_remain = self.capital
                    if order is not None:
                        self.send_order(order)
                        self.handle_order(order)
                    logging.info(f'Cash balance updated: {cash_remain} -> {self.capital}')
                    print(f'Cash:{cash_remain} -> {self.capital}\n')
                except (json.JSONDecodeError, TypeError):
                    logging.error(f"JSON decoding error: {json.JSONDecodeError}. Data: {received}")
                    print("Error processing received data")
                    break

    def handle_order(self, order):
        signal = order['Direction']
        amount = order['Amount']
        if self.price is None:
            logging.error("Price not available for handling order")
            print("Price not available for handling order")
            return
        if signal == 'Buy':
            self.capital -= amount * self.price
        elif signal == 'Sell':
            self.capital += amount * self.price
        logging.info(f"Order handled, new capital: {self.capital}")
        
    def send_order(self, order):
        logging.debug(f"Sending order: {order}")
        self.sock.sendall(bytes(json.dumps(order), "utf-8"))
        logging.info(f"Order sent: {order}")
    
if __name__ == "__main__":
    CrossOverMA_strategy = CrossOverMA(fraction=0.1)
    Momentum_strategy = Momentum()
    # RSI_strategy = RSI()
    BollingerBands_strategy = BollingerBands()
    MeanReversion_strategy = MeanReversionStrategy()
    MACD_strategy = MACDStrategy()
    trading = CrossOverMA_strategy
    client = Client(strat=trading.ProcessMarketDataAndGenerateOrder)
    client._connect()
