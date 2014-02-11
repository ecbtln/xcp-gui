from bitcoinrpc.authproxy import AuthServiceProxy


class BTCAsyncAppClient(AuthServiceProxy):
    def __init__(self, host='localhost', port=8332, rpcuser='bitcoinrpc', rpcpassword='PASSWORD'):
        url = "http://%s:%s@%s:%s" % (rpcuser, rpcpassword, host, port)
        super(BTCAsyncAppClient, self).__init__(url, timeout=5)


    def _async_call(self, action, callback, *args, **kwargs):
        pass

