from interface.root_component import Root
from clients.binance import BinanceWs

if __name__ == '__main__':
    symbols = []  # List of symbols to monitor
    symbol_reader = open('list.txt', 'r')
    rows = symbol_reader.readlines()
    for row in rows:
        symbols.append(row.rstrip())
    print('Starting Stream')
    b = BinanceWs(symbols)
    root = Root(b)
    root.mainloop()
