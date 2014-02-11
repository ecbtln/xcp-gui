from decimal import Decimal as D

MAX_SPINBOX_INT = (2 ** 31) - 1
XCP = 'XCP'


class Satoshi:
    CONSTANT = D(100000000)
    NUM_DECIMALS = int(CONSTANT.log10())
    INVERSE = D(1) / CONSTANT