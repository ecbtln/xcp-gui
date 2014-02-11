from bitcoinrpc.authproxy import AuthServiceProxy
import threading
from callback import CallbackEvent
import traceback
from utils import display_alert

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
                # display alert on main thread
                exception_name = str(e)
                traceback_info = traceback.format_exc()
                CallbackEvent.post(lambda: display_alert("Unexpected request error", traceback_info, exception_name))

        threading.Thread(target=call_api).start()

    def get_wallet_addresses(self, callback):
        self._async_call('listreceivedbyaddress', lambda res: callback([x['address'] for x in res]))

    def get_new_address(self, callback):
        self._async_call('getnewaddress', callback)

