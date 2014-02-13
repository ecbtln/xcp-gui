
# By convention, we will store all asset amounts in memory, precisely how they will be conveyed to the user
# This means divisible assets are divided by 100,000,000, and indivisible assets are left as is.


from constants import Satoshi, XCP, BTC
from decimal import Decimal as D
#TODO: decide consistent ordering of elements in list for each model


class Asset:
    """ Immutable representation of an asset and its properties
    """
    def __init__(self, name, divisible, callable, owner):
        self.name = name
        self.divisible = bool(divisible)  # the api sends them over as ints
        self.callable = bool(callable) if callable is not None else None
        self.owner = owner

    def convert_for_api(self, amount):
        if self.divisible:
            return int(D(amount) * Satoshi.CONSTANT)
        else:
            return int(amount)

    def convert_for_app(self, amount):
        if self.divisible:
            return D(amount) / Satoshi.CONSTANT
        else:
            return D(amount)

    def format_quantity(self, amount):
        """ once we have an amount, as a decimal, we want to be able to convert it to a string, and append decimal places
        that pad it to Satoshi.NUM_DECIMAL places, even if the decimal is not that long"""
        if self.divisible:
            return str(amount.quantize(Satoshi.INVERSE))
        else:
            return str(amount)


class Portfolio:
    """ Immutable representation of an asset portfolio
    """
    def __init__(self, wallet, address, assets, values):
        assert len(assets) == len(values)
        self.wallet = wallet
        self._assets = assets  # just the asset names go here
        for a in assets:
            assert self.get_asset(a) is not None
        # TODO: convert dictionary to object
        # TODO:, perhaps sort alphabetically?
        # Since, the constructor is taking values from the API, we first convert integer values to human-readable ones
        # amounts is a map from asset name to human-readable amount
        self.amounts = {a: self.wallet.get_asset(a).convert_for_app(v) for a, v in zip(assets, values)}
        self.address = address

    def get_asset(self, asset_name):
        return self.wallet.get_asset(asset_name)

    def amount_for_asset(self, asset_name):
        return self.amounts.get(asset_name, 0)

    def owns_asset(self, asset_name):
        asset = self.get_asset(asset_name)
        if asset is None:
            return False
        return self.address == asset.owner

    @property
    def assets(self):
        return [self.get_asset(a) for a in self._assets]


class Wallet:
    def __init__(self, addresses=None):
        self.portfolios = {} # map of addresses to portfolios
        self.assets = {} # some portfolios may share the same assets, just point to these, and map asset name, to object for convenience
        if addresses is None:
            self.addresses = []
        else:
            self.addresses = addresses
        self.active_address_index = None

    def update_portfolios(self, all_assets, portfolios):
        # each asset is listed as a dictionary: with keys 'name', 'divisible', 'callable'
        # each portfolio is listed as a dictionary with keys 'address', 'assets', 'values'
        self.assets = {a['name']: Asset(**a) for a in all_assets}
        # this asset is fixed and should always be available for reference
        self.assets[XCP] = Asset(XCP, True, False, None)
        self.assets[BTC] = Asset(BTC, True, False, None)
        self.portfolios = {}
        for p in portfolios:
            p['wallet'] = self
            portfolio = Portfolio(**p)
            address = p['address']
            assert address in self.addresses
            self.portfolios[address] = portfolio

    def get_asset(self, asset_name):
        return self.assets.get(asset_name, None)

    def update_addresses(self, new):
        old_selected = None if self.active_address_index is None else self.addresses[self.active_address_index]
        self.addresses = new
        if old_selected is not None:
            try:
                idx = new.index(old_selected)
            except ValueError:
                idx = None
        else:
            idx = None
        self.active_address_index = idx

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
        return self.portfolios.get(address, None)



