from gui import PyQtGui
from models import Wallet, Asset
from rpcclient.btc_async_app_client import BTCAsyncAppClient
from rpcclient.xcp_async_app_client import XCPAsyncAppClient
from constants import XCP


class XCPApplication(PyQtGui.QApplication):
    """
    A basic subclass of the QApplication object that provides us with some app-wide state
    """
    def __init__(self, *args, **kwargs):
        super(XCPApplication, self).__init__(*args, **kwargs)
        self.wallet = Wallet()
        self.xcp_client = XCPAsyncAppClient()
        self.btc_client = BTCAsyncAppClient()
        self.LAST_BLOCK = None

    def examine_local_wallet(self, after):
        def cb(res):
            self.wallet.update_addresses(res)
            after()
        self.btc_client.get_wallet_addresses(cb)

    def fetch_initial_data(self, update_wallet_callback_func):
        """
        Fetch the initial data and insert it into our model in the correct format. Because we use callbacks, the
        appearance of this staircase-like method is a bit hideous, but makes the sense if you look at the bottom first.
        Since all callbacks are posted to the main thread, there are no concerns of races.
        """
        wallet = self.wallet

        def fetch_data_after_wallet_update():
            def process_balances(bals):
                portfolios = {}
                assets = set()
                for entry in bals:
                    asset = entry['asset']
                    assets.add(asset)
                    address = entry['address']
                    amount = entry['amount']
                    if address not in portfolios:
                        portfolios[address] = {}
                    p = portfolios[address]
                    p[asset] = p.get(asset, 0) + amount
                # don't get_asset_info for XCP, we already know the info and the RCP does not take well with that request
                if XCP in assets:
                    assets.remove(XCP)

                asset_name_list = list(assets)

                def process_asset_info(asset_info_results):

                    asset_info_list = [{'name': asset_name,
                                        'divisible': res['divisible'],
                                        'callable': res['callable'],
                                        'owner': res['owner']} for asset_name, res in zip(asset_name_list,
                                                                                          asset_info_results)]

                    # now massage the portfolios dictionary to be the desired format of the wallet method
                    new_portfolios = []
                    for address in portfolios:
                        p = portfolios[address]
                        assets = list(p.keys())
                        values = [p[a] for a in assets]
                        new_portfolios.append({'address': address,
                                               'assets': assets,
                                               'values': values})
                    wallet.update_portfolios(asset_info_list, new_portfolios)
                    update_wallet_callback_func(wallet.addresses)

                    # we need to get a list of all the assets and their results (to see what is divisible and what isn't)
                    # and also to suggest to the user when they type an asset to make an order for
                    def process_issuances(issuances):
                        for i in issuances:
                            name = i['asset']
                            if name not in wallet.assets:
                                issuer = i['issuer']
                                divisible = i['divisible']
                                callable = i['callable']
                                wallet.assets[name] = Asset(name, divisible, callable, issuer)
                    self.xcp_client.get_issuances(process_issuances)

                self.xcp_client.get_assets_info(asset_name_list, process_asset_info)

            self.xcp_client.get_balances(wallet.addresses, process_balances)
        self.examine_local_wallet(fetch_data_after_wallet_update)
