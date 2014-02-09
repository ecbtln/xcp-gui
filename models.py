
# By convention, we will store all asset amounts in memory, precisely how they will be conveyed to the user
# This means divisible assets are divided by 100,000,000, and indivisible assets are left as is.


SATOSHI_CONSTANT = 100000000
#TODO: decide consistent ordering of elements in list for each model

class Asset:
    """ Immutable representation of an asset and its properties
    """
    def __init__(self, name, divisible, callable=False):
        self.name = name
        self.divisible = divisible
        self.callable = callable

    def format_for_api(self, amount):
        if self.divisible:
            return int(amount * SATOSHI_CONSTANT)
        else:
            return amount

    def format_for_app(self, amount):
        if self.divisible:
            return float(amount) / SATOSHI_CONSTANT
        else:
            return amount


class Portfolio:
    """ Immutable representation of an asset portfolio
    """
    def __init__(self, wallet, address, assets, values):
        assert len(assets) == len(values)
        self.wallet = wallet
        self.assets = assets  # just the asset names go here
        for a in assets:
            assert self.get_asset(a) is not None
        # TODO: convert dictionary to object
        # TODO:, perhaps sort alphabetically?
        # Since, the constructor is taking values from the API, we first convert integer values to human-readable ones
        # amounts is a map from asset name to human-readable amount
        self.amounts = {a: self.wallet.get_asset(a).format_for_app(v) for a, v in zip(assets, values)}
        self.address = address

    def get_asset(self, asset_name):
        return self.wallet.get_asset(asset_name)

    def amount_for_asset(self, asset_name):
        self.amounts.get(asset_name, 0)


class Wallet:
    def __init__(self, addresses):
        self.portfolios = {} # map of addresses to portfolios
        self.assets = {} # some portfolios may share the same assets, just point to these, and map asset name, to object for convenience
        self.addresses = addresses
        self.active_address_index = None

    def update_portfolios(self, all_assets, portfolios):
        # each asset is listed as a dictionary: with keys 'name', 'divisible', 'callable'
        # each portfolio is listed as a dictionary with keys 'address', 'assets', 'values'
        self.assets = {a['name']: Asset(**a) for a in all_assets}
        self.portfolios = {}
        for p in portfolios:
            p['wallet'] = self
            portfolio = Portfolio(**p)
            address = p['address']
            assert address in self.addresses
            self.portfolios[address] = portfolio

    def get_asset(self, asset_name):
        return self.assets.get(asset_name, None)


    @property
    def active_address(self):
        if len(self.addresses) and self.active_address_index is not None:
            return self.addresses[self.active_address_index]
        return None

    @property
    def active_portfolio(self):
        address = self.active_address
        if address is None:
            return None
        return self.portfolios[address]



