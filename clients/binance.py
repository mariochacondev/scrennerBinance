import json
import typing
from unicorn_binance_websocket_api.manager import BinanceWebSocketApiManager


class BinanceWs:
    def __init__(self, symbols: typing.List[str]):
        self.market_data = dict()
        self.symbols = symbols
        self.binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com-futures")
        self.stream_id = self.binance_websocket_api_manager.create_stream('kline_1m', self.symbols)

        for symbol in symbols:
            self.market_data[symbol] = {'open': float(), 'high': float(), 'low': float(), 'close': float(),
                                        'is_closed': bool, 'highs': list(), 'lows': list(), 'closes': list(),
                                        'opens': list(), 'average_price': list()}

    def run(self, symbol):
        try:
            received_stream_data_json = self.binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
            if received_stream_data_json:
                json_data = json.loads(received_stream_data_json)
                candle_data = json_data.get('data', {})
                message = candle_data.get('k', {})
                if message:
                    if str(symbol.upper()) == str(message.get('s')):
                        self.market_data[symbol]['close'], \
                        self.market_data[symbol]['high'], \
                        self.market_data[symbol]['low'], \
                        self.market_data[symbol]['open'], \
                        self.market_data[symbol]['is_closed'] = message.get('c'), \
                                                                message.get('h'), \
                                                                message.get('l'), \
                                                                message.get('o'), \
                                                                message.get('x')
            if self.binance_websocket_api_manager.binance_api_status['status_code'] is not None:
                print(self.binance_websocket_api_manager.binance_api_status['status_code'])

            stream_global = self.binance_websocket_api_manager.get_stream_statistic(self.stream_id)
            print('RECEIVES PER SECOND', stream_global['stream_receives_per_second'])
        except Exception as e:
            print('run method error: ', e)
