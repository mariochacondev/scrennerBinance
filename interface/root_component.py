import tkinter as tk
from tkinter.messagebox import askquestion
import time
from clients.binance import BinanceWs
from interface.styling import *
from interface.screener_component import Screener
import talib
import numpy


class Root(tk.Tk):
    def __init__(self, binance: BinanceWs):
        super().__init__()
        self.binance = binance
        self.title("Crypto Screener")
        self.protocol("WM_DELETE_WINDOW", self._ask_before_close)
        self.configure(bg=BG_COLOR)
        # Creates and places components at the top and bottom of the left and right frame
        self._screener_frame = Screener(self, bg=BG_COLOR)
        self._screener_frame.pack(side=tk.TOP, padx=10)
        self._update_ui()  # Starts the infinite interface update loop

    def _ask_before_close(self):
        result = askquestion("Confirmation", "Do you really want to exit the application?")
        if result == "yes":
            self.binance.binance_websocket_api_manager.stop_manager_with_all_streams()
            self.destroy()  # Destroys the UI and terminates the program
            print(f'Closing Screener and Stream')

    def _update_ui(self):
        tree = self._screener_frame.tree
        max_samples = 2
        average_number_kandle = 5

        def average_price(last_open, last_high, last_lows, last_close):
            return float((float(last_open) + float(last_high) + float(last_lows) + float(last_close)) / 4)

        def twap(average_price):
            return round(sum(average_price) / len(average_price), 4)

        def fibo_382(high, low):
            return round((float(high) - ((float(high) - float(low)) * 0.382)), 3)

        def bbs(closes_string):
            upperband, middleband, lowerband = talib.BBANDS(numpy.array(closes_string, dtype=float),
                                                            timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
            return upperband, middleband, lowerband

        for symbol in self.binance.symbols:
            data = self.binance.market_data[symbol]
            self.binance.run(symbol)

            if symbol not in self._screener_frame.symbols:
                if data.high is not None:
                    row_data = [data.close, data.high, data.low, data.open, "", "", ""]
                    tree.insert("", tk.END, symbol, text=symbol.upper(), values=row_data)
                    self._screener_frame.symbols.append(symbol)

            if data.is_closed is True:
                tree.set(symbol, column='fibo_382', value=fibo_382(data.high, data.low))
                if len(data.closes) <= 2:
                    data.closes.append(data.close)
                if len(data.highs) <= 2:
                    data.highs.append(data.high)
                if len(data.lows) <= 2:
                    data.lows.append(data.low)
                if len(data.opens) <= 2:
                    data.opens.append(data.open)

            if len(data.closes) and len(data.highs) and len(data.lows) and len(data.opens) == max_samples:
                data.average_price.append(average_price(data.opens[-1], data.highs[-1], data.lows[-1], data.closes[-1]))
                data.closes.pop(0)
                data.highs.pop(0)
                data.lows.pop(0)
                data.opens.pop(0)

            if len(data.average_price) == average_number_kandle:
                tree.set(symbol, column='twap', value=twap(data.average_price))
                data.average_price.pop(0)
                upperband, middleband, lowerband = bbs(data.closes)
                if lowerband[-1] > float(data.close):
                    tree.set(symbol, column='bbs_signal', value='BUY')
                tree.set(symbol, column='bbs_signal', value='HOLD')
                if upperband[-1] < float(data.close):
                    tree.set(symbol, column='bbs_signal', value='SELL')
                tree.set(symbol, column='bbs_signal', value='HOLD')


            tree.set(symbol, column='high', value=data.high)
            tree.set(symbol, column='low', value=data.low)
            tree.set(symbol, column='open', value=data.open)
            tree.set(symbol, column='close', value=data.close)
            print(f'{symbol}: {data}')

        if tree.last_sort is not None and time.time() - 1 > tree.last_auto_sort:
            tree.sort_column(*tree.last_sort)
            tree.last_auto_sort = time.time()
        self.after(400, self._update_ui)
