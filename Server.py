import socket
import threading
import csv
import json
# import argparse
# import sys
import time
# import datetime
import logging

logging.basicConfig(filename='server.log', 
                    level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class Server:
    def __init__(self, host, port, file_path, wait=0.01):
        logging.debug("Initializing server")
        # self.environment = {}
        # self.environment['NoMode'] = {'points': 0}
        # self.environment['Occupancy'] = {'occupancy': 0, 'points': 0}
        self.host = host
        self.port = port
        # self.state = self.environment[opt.mode if opt.mode else 'NoMode']
        self.data_file_path = file_path
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.lock = threading.Lock()
        self.holding = 0
        self.wait = wait

    def listen(self):
        logging.info('Server established and listening')
        self.sock.listen(5)
        while True:
            logging.info('Listening for client connection')
            client, address = self.sock.accept()
            client.settimeout(500)
            threading.Thread(target=self.listenToClient, args=(client, address)).start()
            threading.Thread(target=self.sendStreamToClient, args=(client,)).start()
            # threading.Thread(target=self.sendStreamToClient, args=(client, sendCSVfile())).start()

    def handle_client_answer(self, obj):
        logging.debug(f"Handling client answer: {obj}")
        print(obj)
        with self.lock:
            holding = self.holding
            if obj['Direction'] == 'Buy':
                self.holding += obj['Amount']
            elif obj['Direction'] == 'Sell':
                self.holding -= obj['Amount']
            print(f'Holdings:|{holding} -> {self.holding}\n')
            logging.info(f'Holdings:|{holding} -> {self.holding}')

    def listenToClient(self, client, address):
        logging.debug(f"Listening to client {address}")
        size = 1024
        while True:
            try:
                data = str(client.recv(size), "utf-8").replace("'", '"')
                if data:
                    # Set the response to echo back the recieved data
                    a = json.loads(data.rstrip('\n\r '))
                    self.handle_client_answer(a)
                else:
                    raise ConnectionError("Client Disconnected")
            except Exception as e:
                logging.error(f"Unexpected Error with client {address}: {e}")
                print(f"Unexpected Error: {e}")
                client.close()
                return False

    def sendStreamToClient(self, client):
        logging.debug("Sending stream to client")
        buffer = self.sendCSVfile()
        for i in buffer:
            print(i)
            with self.lock:
                i['Holdings'] = self.holding
            try:
                client.send((self.convertStringToJSON(i) + '\n').encode('utf-8'))
                time.sleep(self.wait)
            except socket.error as e:
                logging.error(f'End of Streaming due to error: {e}')
                print(f'End of Streaming due to error: {e}')
                client.close()
                return False
        return False

    def convertStringToJSON(self, st):
        return json.dumps(st)

    def sendCSVfile(self):
        logging.debug("Sending CSV data")
        with open(self.data_file_path, 'r') as data:
            csv_reader = csv.DictReader(data)
            output = [row for row in csv_reader]
        return output

if __name__ == '__main__':
    Server = Server('127.0.0.1', 9999, 'QQQ.csv')
    Server.listen()
