from decimal import Decimal as D

MAX_SPINBOX_INT = (2 ** 31) - 1
XCP = 'XCP'


class Satoshi:
    CONSTANT = D(100000000)
    NUM_DECIMALS = int(CONSTANT.log10())
    INVERSE = D(1) / CONSTANT


#TODO: remove me
BTC_ADDRESSES = ['mz8qzVaH8RaVp2Rq6m8D2dTiSFirhFf4th',
                 'mzdtcqgLKR6HiartUL19wD3HRERX7RzELz',
                 'mwR7RbuNwgwX9cfHKeS7Jgmydn1KtFKH1X',
                 'mrutZKJ1XrNdAwLhsKfTUmZwdk1shhsRWw']