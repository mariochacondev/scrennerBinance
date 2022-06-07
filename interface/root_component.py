import tkinter as tk
from tkinter.messagebox import askquestion
import time
import logging

from clients.binance import BinanceWs

from interface.styling import *
from interface.screener_component import Screener

logger = logging.getLogger()  # This will be the same logger object as the one configured in main.py


class Root(tk.Tk):
    def __init__(self, binance: BinanceWs):
        super().__init__()

        self.binance = binance

        self.title("Alert System")
        self.protocol("WM_DELETE_WINDOW", self._ask_before_close)

        self.configure(bg=BG_COLOR)

        # Creates and places components at the top and bottom of the left and right frame

        self._screener_frame = Screener(self, bg=BG_COLOR)
        self._screener_frame.pack(side=tk.TOP, padx=10)

        # Create a Menu

        self.main_menu = tk.Menu(self)
        self.configure(menu=self.main_menu)


        self._update_ui()  # Starts the infinite interface update loop

    def _ask_before_close(self):

        """
        Triggered when the user click on the Close button of the interface.
        This lets you have control over what's happening just before closing the interface.
        :return:
        """

        result = askquestion("Confirmation", "Do you really want to exit the application?")
        if result == "yes":
            self.binance.binance_websocket_api_manager.stop_manager_with_all_streams()
            self.destroy()  # Destroys the UI and terminates the program


    def _update_ui(self):

        """
        Called by itself every 500 milliseconds. It is similar to an infinite loop but runs within the same Thread
        as .mainloop() thanks to the .after() method, thus it is "thread-safe" to update elements of the interface
        in this method. Do not update Tkinter elements from another Thread like a websocket thread.
        :return:
        """

        tree = self._screener_frame.tree


        try:
            for symbol in self.binance.symbols:

                data = self.binance.market_data[symbol]

                self.binance.run(symbol)


                if symbol not in self._screener_frame.symbols:
                    if data['high'] is not None:
                        row_data = [data['close'], data['high'], data['low'], data['open'], '?']
                        tree.insert("", tk.END, symbol, text=symbol.upper(), values=row_data)
                        self._screener_frame.symbols.append(symbol)


                if data['is_closed'] is True:
                    self.highs, self.lows, self.closes, self.opens, self.avg_price, self.twap = list(), list(), list(), list(), list(), list()
                    self.highs.append(data['high'])
                    self.lows.append(data['low'])
                    self.closes.append(data['close'])
                    self.opens.append(data['open'])

                    def avgPrice():
                        avr = float(self.opens[-1]) + float(self.highs[-1]) + float(self.lows[-1]) + float(
                            self.closes[-1]) / 4
                        self.avg_price.append(float(avr))
                        print('avg_price: ', self.avg_price)

                    def tWap(avg_price):
                        twap = sum(avg_price) / len(avg_price)
                        self.twap.append(twap)
                        print('twap : ', self.twap)

                    max_samples = 2
                    average_number_kandle = 5

                    if len(self.closes) and len(self.highs) and len(self.lows) and len(self.opens) == max_samples:
                        avgPrice()

                        if len(self.avg_price) == average_number_kandle:
                            tWap(self.avg_price)

                            self.avg_price.pop(0)

                            self.closes.pop(0)
                            self.highs.pop(0)
                            self.lows.pop(0)
                            self.opens.pop(0)


                    tree.set(symbol, column='twap', value=self.twap)
                pass

                if data['high'] is not None:
                    tree.set(symbol, column='high', value=data['high'])
                    tree.set(symbol, column='low', value=data['low'])
                    tree.set(symbol, column='open', value=data['open'])
                    tree.set(symbol, column='close', value=data['close'])

                pass

        except RuntimeError:
            pass


        if tree.last_sort is not None and time.time() - 1 > tree.last_auto_sort:
            tree.sort_column(*tree.last_sort)  # Keep the last sorting
            tree.last_auto_sort = time.time()  # Avoid sorting too often

        self.after(400, self._update_ui)