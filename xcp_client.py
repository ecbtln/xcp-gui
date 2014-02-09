

import json
import requests
from requests.auth import HTTPBasicAuth
from exceptions import InvalidRPCMethod, InvalidRPCArguments, RPCError

BTC_ADDRESSES = ['mz8qzVaH8RaVp2Rq6m8D2dTiSFirhFf4th', 'mzdtcqgLKR6HiartUL19wD3HRERX7RzELz', 'mwR7RbuNwgwX9cfHKeS7Jgmydn1KtFKH1X']


class XCPClient(object):
    VALID_API_METHODS = {'get_address', 'xcp_supply', 'get_balances', 'get_bets', 'get_bet_matches', 'get_broadcasts',
                         'get_btcpays', 'get_burns', 'get_cancels', 'get_credits', 'get_debits', 'get_dividends',
                         'get_issuances', 'get_orders', 'get_order_matches', 'get_sends', 'get_asset_info', 'do_bet',
                         'do_broadcast', 'do_btcpay', 'do_burn', 'do_cancel', 'do_dividend', 'do_issuance', 'do_order',
                         'do_send'}

    def __init__(self, host='localhost', port=4000, rpcuser='rpcuser', rpcpassword='rpcpassword'):
        self.url = 'http://%s:%d/jsonrpc/' % (host, port)
        self.headers = {'content-type': 'application/json'}
        self.auth = HTTPBasicAuth(rpcuser, rpcpassword)

    def _call_api(self, method, params=None):
        if method not in self.VALID_API_METHODS:
            raise InvalidRPCMethod("%s is not a valid RPC method" % method)

        if params is None:
            params = {}

        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0
        }

        response = requests.post(self.url, data=json.dumps(payload), headers=self.headers, auth=self.auth)
        if response:
            js = response.json()
            if 'result' in js:
                return js['result']
            else:
                assert 'error' in js
                raise InvalidRPCArguments(str(js['error']))
        else:
            raise RPCError("Unable to load request at URL: %s, with payload: %s" % (self.url, str(payload)))

    def __getattr__(self, item):
        if item in self.VALID_API_METHODS:
            # only allow *args or **kwargs, but not both
            def api_call(*args, **kwargs):
                if len(args) and len(kwargs):
                    raise InvalidRPCArguments("The api call can take either arguments, or keywords, but not both.")
                return self._call_api(item, args or kwargs or None)
            return api_call
        else:
            return super(XCPClient, self).__getattribute__(item)



if __name__ == '__main__':
    client = XCPClient(port=14000)

    # get balances for all assets, including xcp, for a given address
    print(client.xcp_supply())
    print(client.get_balances({'field': 'address', 'op': '==', 'value': BTC_ADDRESSES[0]}))