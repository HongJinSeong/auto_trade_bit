import numpy as np

def get_coin_only_USDT(FM_conids):
    USDT_LIST=[]
    for coin_nm in FM_conids:
        if coin_nm.endswith('/USDT'):
            USDT_LIST.append(coin_nm)

    return USDT_LIST

def get_only_my_position(positions):
    my_position=[]
    for pos in positions:
        if pos['initialMargin']!='0':
            my_position.append(pos)

    return my_position

def position_symbol(pos):
    symbol=pos.split(pos[-4:])[0]+'/'+pos[-4:]

    return symbol