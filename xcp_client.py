__author__ = 'elubin'

import json
import requests
from requests.auth import HTTPBasicAuth
from exceptions import InvalidRPCMethod


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
            "method" : method,
            "params" : params,
            "jsonrpc" : "2.0",
            "id" : 0
        }

        return requests.post(self.url, data=json.dumps(payload), headers=self.headers, auth=self.auth).json()

    def __getattr__(self, item):
        if item in self.VALID_API_METHODS:
            return lambda **kwargs: self._call_api(item, kwargs)
        else:
            return super(XCPClient, self).__getattribute__(item)