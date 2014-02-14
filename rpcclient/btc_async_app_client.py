from bitcoinrpc.authproxy import AuthServiceProxy
import threading
from callback import CallbackEvent
from rpcclient.common import report_exception
from constants import BTC, BTC_CONNECTION_TIMEOUT
import counterpartyd.lib.config as config


def url_for_client(host=None, port=None, rpcuser=None, rpcpassword=None):
    if host is None:
        host = config.BITCOIND_RPC_CONNECT
    if port is None:
        port = config.BITCOIND_RPC_PORT
    if rpcuser is None:
        rpcuser = config.BITCOIND_RPC_USER
    if rpcpassword is None:
        rpcpassword = config.BITCOIND_RPC_PASSWORD
    return "http://%s:%s@%s:%s" % (rpcuser, rpcpassword, host, port)

class BTCAsyncAppClient(AuthServiceProxy):
    def __init__(self, host=None, port=None, rpcuser=None, rpcpassword=None):
        url = url_for_client(host, port, rpcuser, rpcpassword)
        super(BTCAsyncAppClient, self).__init__(url, timeout=BTC_CONNECTION_TIMEOUT)

    def _async_call(self, action, callback, *args, **kwargs):
        def call_api():
            try:
                result = getattr(self, action)(*args, **kwargs)
                if callback:
                    # perform callback on main thread
                    CallbackEvent.post(lambda: callback(result))
            except Exception as e:
                report_exception(BTC, e)

        threading.Thread(target=call_api).start()

    def get_wallet_addresses(self, callback):
        self._async_call('listreceivedbyaddress', lambda res: callback([x['address'] for x in res]), 0, False)

    def get_new_address(self, callback):
        self._async_call('getnewaddress', callback)

