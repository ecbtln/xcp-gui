
# By convention, we will store all asset amounts in memory, precisely how they will be conveyed to the user
# This means divisible assets are divided by 100,000,000, and indivisible assets are left as is.


SATOSHI_CONSTANT = 100000000


class Asset:
    def __init__(self, name, divisible, callable=False):
        self.name = name
        self.divisible = divisible
        self.callable = callable

    def format_for_api(self, amount):
        if self.divisible:
            return int(amount * SATOSHI_CONSTANT)
        else:
            return amount


class Portfolio:
    def __init__(self, address):
        self.portfolio = []
        self.address = address




class Wallet:
    def __init__(self, addresses):
        self.portfolios = {}
        self.addresses = addresses




