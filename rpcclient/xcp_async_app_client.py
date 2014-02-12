import threading
from requests.exceptions import ConnectionError
from rpcclient.xcp_client import XCPClient
from utils import AtomicInteger
from exceptions import InvalidRPCArguments, RPCError
from callback import CallbackEvent
from rpcclient.common import report_exception
from constants import XCP


class XCPAsyncAppClient(XCPClient):
    """
    A subclass of the XCPClient that defines methods, with restricted parameters and asynchronous callbacks
    to be used directly by the app
    """
    def _async_api_call(self, method, params=None, callback=None):
        def call_api():
            try:
                result = self._call_api(method, params)
                if callback:
                    # perform callback on main thread
                    CallbackEvent.post(lambda: callback(result))
            except (ConnectionError, InvalidRPCArguments, RPCError) as e:
                report_exception(XCP, e)

        threading.Thread(target=call_api).start()

    def get_balances(self, btc_addresses, callback):
        self._async_api_call('get_balances', {'filters': [{'field': 'address',
                                                           'op': '==',
                                                           'value': x} for x in btc_addresses],
                                              'filterop': 'or'},
                             callback)

    def get_asset_info(self, asset, callback):
        self._async_api_call('get_asset_info', asset, callback)

    def _call_multiple(self, requests, callback):
        """
        Each element in the requests array is a lambda, that takes in one argument, the callback function
        """
        results = [None] * len(requests)
        val = AtomicInteger(len(requests))

        #num_left = len(requests)  # TODO: needs to be atomic integer
        for i, r in enumerate(requests):
            def c_back(j, result):
                results[j] = result
                if val.decrementAndGet() == 0:
                    callback(results)

            # this is needed in python to make sure the value of i is copied. Essentially, we wrap the call to c_back
            # in a lambda, which is immediately called with the desired value
            r((lambda i: lambda res: c_back(i, res))(i))

    def get_assets_info(self, assets, callback):
        """
        Returns an array of assets, by individually calling the get_asset_info method for each asset and then executing
        the global callback when the last has completed
        """
        if len(assets) == 0:
            callback([])
        elif len(assets) == 1:
            # the caller is expecting an array, so wrap the callback parameter in an array
            self.get_asset_info(assets[0], lambda res: callback([res]))
        else:
            self._call_multiple([lambda resp: self.get_asset_info(a, resp) for a in assets], callback)

    def do_send(self, source, destination, quantity, asset, callback):
        self._async_api_call('do_send', [source, destination, quantity, asset], callback)

    def get_orders(self, btc_addresses, callback):
        self._async_api_call('get_orders', {'filters': [{'field': 'source',
                                                         'op': '==',
                                                         'value': x} for x in btc_addresses],
                                            'filterop': 'or',
                                            'show_expired': False,
                                            'order_by': 'block_index',
                                            'order_dir': 'desc'}, callback)

    def get_order_matches(self, callback):
        self._async_api_call('get_order_matches', {'is_mine': True,
                                                   'order_by': 'block_index',
                                                   'order_dir': 'desc'}, callback)
if __name__ == '__main__':
    client = XCPAsyncAppClient(port=14000)
    client.get_assets_info(['IIII', 'WEED'], lambda x: print(x))
    BTC_ADDRESSES = ['mz8qzVaH8RaVp2Rq6m8D2dTiSFirhFf4th',
                    'mzdtcqgLKR6HiartUL19wD3HRERX7RzELz',
                    'mwR7RbuNwgwX9cfHKeS7Jgmydn1KtFKH1X',
                    'mrutZKJ1XrNdAwLhsKfTUmZwdk1shhsRWw']
    client.get_balances(BTC_ADDRESSES, lambda x: print(x))