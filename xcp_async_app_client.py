from xcp_client import XCPClient
import threading
from utils import AtomicInteger, display_alert
from requests.exceptions import ConnectionError
from exceptions import InvalidRPCArguments, RPCError

class XCPAsyncAppClient(XCPClient):
    """
    A subclass of the XCPClient that defines methods, with restricted parameters and asynchronous callbacks
    to be used directly by the app
    """
    def _async_api_call(self, method, params=None, callback=None):
        def call_api():
            #TODO: present alert when connection fails
            #try:
            result = self._call_api(method, params)
            if callback:
                callback(result)
            #except (ConnectionError, InvalidRPCArguments, RPCError) as e:
                #display_alert("Unexpected error", str(e))

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
        val = AtomicInteger(len(request))

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

if __name__ == '__main__':
    client = XCPAsyncAppClient(port=14000)
    client.get_assets_info(['IIII', 'WEED'], lambda x: print(x))
    from constants import BTC_ADDRESSES
    client.get_balances(BTC_ADDRESSES, lambda x: print(x))