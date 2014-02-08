from xcp_client import XCPClient, BTC_ADDRESS
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

    def get_balances(self, btc_address, callback):
        self._async_api_call('get_balances', [{'field': 'address', 'op': '==', 'value': btc_address}], callback)

