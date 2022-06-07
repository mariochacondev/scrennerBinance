import logging
import os
import datetime
import csv

# import binance

from interface.root_component import Root
from clients.binance import BinanceWs


if not os.path.exists("logs"):
    os.makedirs("logs")

current_day = datetime.datetime.utcnow().strftime('%Y-%m-%d')

if not os.path.exists(f"logs/{current_day}"):
    os.makedirs(f"logs/{current_day}")

logger = logging.getLogger()

logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.WARNING)

file_handler = logging.FileHandler(f"logs/{current_day}/info_{datetime.datetime.utcnow().strftime('%H%M%S')}.log",
                                   mode="a",
                                   encoding="utf-8")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)


if __name__ == '__main__':

    channels = []
    symbols = []  # List of symbols to monitor

    with open('list.csv') as csv_file:
        csv_reader = csv.reader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                symbols.append(row[0])
                line_count += 1

    print(f'Main starting streams ... ')

    b = BinanceWs(channels, symbols)
    root = Root(b)
    root.mainloop()
