from decimal import Decimal as D

MAX_SPINBOX_INT = (2 ** 31) - 1
XCP = 'XCP'
BTC = 'BTC'
BTC_CONNECTION_TIMEOUT = 15
MAX_BYTES_ASSET_DESCRIPTION = 52
MIN_LENGTH_ASSET_NAME = 4

class Satoshi:
    CONSTANT = D(100000000)
    NUM_DECIMALS = int(CONSTANT.log10())
    INVERSE = D(1) / CONSTANT