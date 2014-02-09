from xcp_client import XCPClient, BTC_ADDRESSES
import threading

class XCPAsyncAppClient(XCPClient):
    """
    A subclass of the XCPClient that defines methods, with restricted parameters and asynchronous callbacks
    to be used directly by the app
    """
    def _async_api_call(self, method, params=None, callback=None):
        def call_api():
            result = self._call_api(method, params)
            if callback:
                callback(result)

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
        results = [] * len(request)
        l = threading.Semaphore()

        num_left = len(requests) #TODO: needs to be atomic integer
        for i, r in enumerate(requests):
            def c_back(result):

                results[i] = result
                #TODO: lock
                num_left -= 1
                if num_left == 0:
                    callback(results)
                #TODO: unlock
            r(c_back)

    def get_assets_info(self, assets, callback):
        """
        Returns an array of assets, by individually calling the get_asset_info method for each asset and then executing
        the global callback when the last has completed
        """
        if len(assets) == 0:
            return []
        self._call_multiple([lambda resp: self.get_asset_info(a, resp) for a in assets], callback)



    def do_send(self, source, destination, quantity, asset, callback):
        self._async_api_call('do_send', [source, destination, quantity, asset], callback)