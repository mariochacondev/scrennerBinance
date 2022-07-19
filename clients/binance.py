import json
import typing
from unicorn_binance_websocket_api.manager import BinanceWebSocketApiManager
from pydantic import BaseModel
from typing import Optional


class MarketData(BaseModel):
    open: Optional[float] = 0
    high: Optional[float] = 0
    low: Optional[float] = 0
    close: Optional[float] = 0
    is_closed: Optional[bool] = 0
    highs: Optional[list[float]] = []
    lows: Optional[list[float]] = []
    closes: Optional[list[float]] = []
    opens: Optional[list[float]] = []
    average_price: Optional[list[float]] = []


class BinanceWs:
    def __init__(self, symbols: typing.List[str]):
        self.market_data = dict()
        self.symbols = symbols
        self.binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com-futures")
        self.stream_id = self.binance_websocket_api_manager.create_stream('kline_1m', self.symbols)

        for symbol in symbols:
            self.market_data[symbol] = MarketData()

    def run(self, symbol):
        try:
            received_stream_data_json = self.binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
            if received_stream_data_json:
                json_data = json.loads(received_stream_data_json)
                candle_data = json_data.get('data', {})
                message = candle_data.get('k', {})
                if message:
                    if str(symbol.upper()) == str(message.get('s')):
                        self.market_data[symbol] = MarketData(close=message.get('c'),
                                                                high=message.get('h'),
                                                                low=message.get('l'),
                                                                open=message.get('o'),
                                                                is_closed=message.get('x'))
            if self.binance_websocket_api_manager.binance_api_status['status_code'] is not None:
                print(self.binance_websocket_api_manager.binance_api_status['status_code'])
            stream_global = self.binance_websocket_api_manager.get_stream_statistic(self.stream_id)
            print('RECEIVES PER SECOND', stream_global['stream_receives_per_second'])
        except Exception as e:
            print('run method error: ', e)
