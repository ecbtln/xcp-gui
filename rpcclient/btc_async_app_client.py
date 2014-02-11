from bitcoinrpc.authproxy import AuthServiceProxy
import threading
from callback import CallbackEvent
from rpcclient.common import report_exception
from constants import BTC

class BTCAsyncAppClient(AuthServiceProxy):
    def __init__(self, host='localhost', port=8332, rpcuser='bitcoinrpc', rpcpassword='PASSWORD'):
        url = "http://%s:%s@%s:%s" % (rpcuser, rpcpassword, host, port)
        super(BTCAsyncAppClient, self).__init__(url, timeout=5)


    def _async_call(self, action, callback, *args, **kwargs):
        def call_api():
            try:
                result = getattr(self, action)(*args, **kwargs)
                if callback:
                    # perform callback on main thread
                    CallbackEvent.post(lambda: callback(result))
            except ConnectionRefusedError as e:
                report_exception(BTC, e)

        threading.Thread(target=call_api).start()

    def get_wallet_addresses(self, callback):
        self._async_call('listreceivedbyaddress', lambda res: callback([x['address'] for x in res]))

    def get_new_address(self, callback):
        self._async_call('getnewaddress', callback)

