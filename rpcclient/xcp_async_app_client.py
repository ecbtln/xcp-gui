import threading
from requests.exceptions import ConnectionError
from rpcclient.xcp_client import XCPClient
from utils import AtomicInteger
from exceptions import InvalidRPCArguments, RPCError
from callback import CallbackEvent
from rpcclient.common import report_exception
from constants import XCP, BTC

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
        if len(btc_addresses) == 0:
            return []
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
            # need to wrap this lambda lambda crap so that python doesn't just distribute the same (last) element
            # of the assets list to all the lambdas when they are called
            self._call_multiple([(lambda asset: lambda resp: self.get_asset_info(asset, resp))(a) for a in assets], callback)

    def do_send(self, source, destination, quantity, asset, callback):
        self._async_api_call('do_send', [source, destination, quantity, asset], callback)

    def do_issuance(self, source, quantity, asset, divisible, description, callable=False, call_date=None, call_price=None, callback=None):
        info = {'source': source,
                'quantity': quantity,
                'asset': asset,
                'divisible': int(divisible),
                'description': description,
                'callable': int(callable),
                'call_date': call_date,
                'call_price': call_price}

        self._async_api_call('do_issuance', info, callback)

    def do_transfer_issuance(self, source, asset, divisible, transfer_destination, callback):
        self._async_api_call('do_issuance', {'source': source,
                                             'quantity': 0,
                                             'asset': asset,
                                             'divisible': int(divisible),
                                             'transfer_destination': transfer_destination}, callback)

    def do_dividend(self, source, quantity_per_unit, asset, callback):
        self._async_api_call('do_dividend', [source, quantity_per_unit, asset], callback)

    def do_order(self, source, give_quantity, give_asset, get_quantity, get_asset, expiration, fee_required,
                 fee_provided, callback):
        self._async_api_call('do_order', [source, give_quantity, give_asset, get_quantity, get_asset, expiration, fee_required, fee_provided], callback)

    def do_cancel(self, offer_hash, callback):
        self._async_api_call('do_cancel', [offer_hash], callback)


    def do_btcpay(self, order_match_id, callback):
        self._async_api_call('do_btcpay', [order_match_id], callback)
    #def do_callback(self, source, asset, fraction_per):

    def get_orders(self, btc_addresses, callback):
        self._async_api_call('get_orders', {'filters': [{'field': 'source',
                                                         'op': '==',
                                                         'value': x} for x in btc_addresses],
                                            'filterop': 'or',
                                            'show_expired': False,
                                            'order_by': 'block_index',
                                            'order_dir': 'desc',
                                            'is_valid': True},
                             callback)

    def get_order_matches(self, callback):
        self._async_api_call('get_order_matches', {'is_mine': True}, callback)

    # def get_btcpay_order_matches(self, callback):
    #     self._async_api_call('get_order_matches', {'order_by': 'tx0_index',
    #                                                'order_dir': 'desc'}, callback)

    def get_issuances(self, callback):
        self._async_api_call('get_issuances', [], callback)
