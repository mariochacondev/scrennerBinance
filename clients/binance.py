import json
import typing
import logging
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager

logger = logging.getLogger()


class BinanceWs:
    def __init__(self, channels, symbols: typing.List[str]):
        self.market_data = dict()
        self.symbols = symbols


        tf = 'kline_1m'
        self.binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com-futures")
        stream = self.binance_websocket_api_manager.create_stream(tf, self.symbols)
        self.binance_websocket_api_manager.subscribe_to_stream(stream, channels, self.symbols)


        for symbol in symbols:
            self.market_data[symbol] = {'open': None, 'high': None, 'low': None, 'close': None, 'is_closed': bool}




    def run(self, symbol):
        try:
            received_stream_data_json = self.binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
            if received_stream_data_json:
                json_data = json.loads(received_stream_data_json)
                candle_data = json_data.get('data', {})
                message = candle_data.get('k', {})
                if message:
                    if str(symbol.upper()) == str(message.get('s')):
                        self.market_data[symbol]['close'] = message.get('c')
                        self.market_data[symbol]['high'] = message.get('h')
                        self.market_data[symbol]['low'] = message.get('l')
                        self.market_data[symbol]['open'] = message.get('o')
                        self.market_data[symbol]['is_closed'] = message.get('x')
                        print(message.get('s'), self.market_data[symbol])
                pass

        except Exception as e:
            print('run method error: ', e)





