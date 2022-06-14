import csv
from interface.root_component import Root
from clients.binance import BinanceWs

if __name__ == '__main__':
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
    print('Starting Stream')
    b = BinanceWs(symbols)
    root = Root(b)
    root.mainloop()
