############코인 자동거래 스타또~!##########

###########      PROCESS         ##########
#   1. 바이낸스 선물거래소의 계좌정보와 모든 코인을 가져오고 기본적인 global 변수 set
#   2. 3개월 미만 코인은 제외
#   3. 기본 loss-trailing 기능만 추가 (TP를 널널하게 잡아야할듯?)
#   4. 구매로직 이전에 내가 생각하는 로직으로 주문을 추천하는것 부터 구현

import os
import ccxt
import numpy as np
from utility.utils import *
import threading
import time
import talib
import telegram
#### real net api key  F8ggtteO478dbKzLn0Ahr9ruyA4IFuYO2NsPe3eEpdP6W2RPf9uALWl6rwBcHZYU
#### real net secret key 1x963w68KlXdDzlIzTW7jig591nqcQeb6SNvroHX1wP6GQZXGNfgIsFbTPdGcDLr
#### telegram key 1754886045:AAEBQKHUpzSq3YWptBV_27V_Bw-X8kd7pBE

#텔레그램 봇 셋팅
tel_token='1754886045:AAEBQKHUpzSq3YWptBV_27V_Bw-X8kd7pBE'
bot=telegram.Bot(token=tel_token)
chat_id=1063955377


symbols=[]
##최초 거래대상 코인들의 이름만 가져옴 (비트를 제외한 모든 코인)
binance = ccxt.binance({
                "options": {"defaultType": "future"},
                "timeout": 30000,
                "apiKey": "F8ggtteO478dbKzLn0Ahr9ruyA4IFuYO2NsPe3eEpdP6W2RPf9uALWl6rwBcHZYU",
                "secret": "1x963w68KlXdDzlIzTW7jig591nqcQeb6SNvroHX1wP6GQZXGNfgIsFbTPdGcDLr",
                "enableRateLimit": True,

            })
datas=binance.load_markets()

for key,val in datas.items():
    #거래단위가 테더이면서 개당 너무 비싼 코인이 아닌경우 (5배율 당겼을 때 최소 구매가능한.. ==> seed가 늘어나면 조정)
    if key.endswith('/USDT') and not key.startswith('BTC') and not key.startswith('YFI'):
        symbols.append(key)

balance =  binance.fetch_balance()

#사용가능한 돈
left_M=float(balance['USDT']['free'])*0.1

#region trailing loss
def loss_trailing():
    while True:
        try:
            binance = ccxt.binance({
                "options": {"defaultType": "future"},
                "timeout": 30000,
                "apiKey": "F8ggtteO478dbKzLn0Ahr9ruyA4IFuYO2NsPe3eEpdP6W2RPf9uALWl6rwBcHZYU",
                "secret": "1x963w68KlXdDzlIzTW7jig591nqcQeb6SNvroHX1wP6GQZXGNfgIsFbTPdGcDLr",
                "enableRateLimit": True,

            })

            balance =  binance.fetch_balance()

            mypositions=get_only_my_position(balance['info']['positions'])

            if len(mypositions)==0:
                print('No position')

            #기준가격
            for idx,position in enumerate(mypositions):
                pos=''
                ## 사이즈에 마이너스인지 아닌지를 통해서 long short 구분
                if position['positionAmt'][0]=='-':
                    pos='S'
                else:
                    pos='L'
                levearge=float(position['leverage'])
                symbol=position_symbol(position['symbol']) #symbol name
                pos_price=float(position['entryPrice']) #포지션 가격
                price=float(binance.fetch_ticker(symbol)['last'])  #현재가

                orders =binance.fetchOpenOrders(symbol)
                for order in orders:
                    if order['type']=='stop_market':
                        stop_order=order
                if 'stop_order' in locals():
                    stopprice=float(stop_order['stopPrice'])

                if pos=='S':
                    print(symbol+' Short position')
                    if (1-(0.03/levearge))*pos_price > price:
                        if 'stop_order' in locals():
                            #레버지 기준 stop_price와
                            if stopprice>price * (1 + (0.08 / levearge)):
                                binance.cancel_order(stop_order['id'],symbol)
                                binance.create_order(symbol, 'stop_market', side='buy', amount=float(position['positionAmt'][1:]),params={'stopPrice': price * (1 + (0.03 / levearge))})
                                bot.send_message(chat_id=chat_id, text=symbol+' short position 익절')
                        else:
                            binance.create_order(symbol,'stop_market',side='buy',amount=float(position['positionAmt'][1:]),params={ 'stopPrice': price *(1+(0.01/levearge))})
                            bot.send_message(chat_id=chat_id, text=symbol + ' short position 익절')
                    if pos_price*1.02<price:
                        sell_price=None
                        binance.create_order(symbol, 'market', side='buy',amount=float(position['positionAmt'][1:]),price=sell_price)
                        bot.send_message(chat_id=chat_id, text=symbol + ' short position 손절')


                else:
                    print(symbol + ' Long position')
                    if (1+(0.03 / levearge)) * pos_price < price :
                        if 'stop_order' in locals():
                            if stopprice<price * (1 - (0.08 / levearge)):
                                 binance.cancel_order(stop_order['id'], symbol)
                                 binance.create_order(symbol, 'stop_market', side='sell', amount=float(position['positionAmt']),params={'stopPrice': price * (1 - (0.03 / levearge))})
                                 bot.send_message(chat_id=chat_id, text=symbol + ' long position 익절')
                        else:
                            binance.create_order(symbol, 'stop_market', side='sell', amount=float(position['positionAmt']),
                                                 params={'stopPrice': price * (1 - (0.01 / levearge))})
                            bot.send_message(chat_id=chat_id, text=symbol + ' long position 익절')
                    if pos_price*1.02>price:
                        sell_price=None
                        binance.create_order(symbol, 'market', side='sell',amount=float(position['positionAmt'][1:]),price=sell_price)
                        bot.send_message(chat_id=chat_id, text=symbol + ' long position 손절')
            time.sleep(5)
        except:
            print('error!')
            binance = ccxt.binance({
                "options": {"defaultType": "future"},
                "timeout": 30000,
                "apiKey": "F8ggtteO478dbKzLn0Ahr9ruyA4IFuYO2NsPe3eEpdP6W2RPf9uALWl6rwBcHZYU",
                "secret": "1x963w68KlXdDzlIzTW7jig591nqcQeb6SNvroHX1wP6GQZXGNfgIsFbTPdGcDLr",
                "enableRateLimit": True,

            })
#endregion

#region 자동매매 ver.1 RSI 기준
# 이더리움 비트 제외하고 5분봉 기준 rsi가 75을 넘고 하락 OR 25를 넘고 상승인 경우에 TP 3% SL -3%기준으로 set하고 거래 하도록 진행
# 익절 - TP 도달 OR trailing에 의해서 레버리지를 고려한 1%로 익절 진행
# 손절 - SL 도달 기준
# 한번 포지션을 가져간 종목은 익절이나 손절에 의해 해당 position 종료전까지 거래 X
# 레버리지 5배로 set하여 돌리기 ==> 레버리지나 TP SL은 해보면서 log쌓은이후에 조정해보는걸로..
def AUTO_trading():
    while True:
        try:
            binance = ccxt.binance({
                "options": {"defaultType": "future"},
                "timeout": 30000,
                "apiKey": "F8ggtteO478dbKzLn0Ahr9ruyA4IFuYO2NsPe3eEpdP6W2RPf9uALWl6rwBcHZYU",
                "secret": "1x963w68KlXdDzlIzTW7jig591nqcQeb6SNvroHX1wP6GQZXGNfgIsFbTPdGcDLr",
                "enableRateLimit": True,

            })

            balance =  binance.fetch_balance()

            #사용가능한 돈
            M=float(balance['USDT']['free'])

            #거래 타겟
            trade_targets = symbols.copy()

            #포지션 체크용 (이미 포지션 보유중인 코인은 제거해야함)
            mypositions=get_only_my_position(balance['info']['positions'])

            #최대 동시 포지션보유 10개까지 
            if len(mypositions)<11:
                #포지션있으면 거래 타겟에서 제거
                for mypo in mypositions:
                    trade_targets.remove(mypositions)


                #거래 마진을 위해서 항상 전체 비용의 10%남겨둠
                if M>left_M:
                    #symbom별로 돌면서 거래 할만한 친구들 찾음
                    #한번에 15분봉 500개 들고옴 약 5일치
                    #이걸로 RSI 계산해야함 그리고 첫번째 값의 종가는 현재값임
                    #candle_data array의 4번째 값만 사용하여 rsi 계산하여 처리해야함
                    #rsi 값 뽑아본 이후에 추가하는걸로..
                    for target_symbol in trade_targets:
                        candle_data=binance.fetch_ohlcv(target_symbol,'15m')
                        #binance.create_order()
                        print('aaa')
            time.sleep(5)
        except:
            print('error!')
            binance = ccxt.binance({
                "options": {"defaultType": "future"},
                "timeout": 30000,
                "apiKey": "F8ggtteO478dbKzLn0Ahr9ruyA4IFuYO2NsPe3eEpdP6W2RPf9uALWl6rwBcHZYU",
                "secret": "1x963w68KlXdDzlIzTW7jig591nqcQeb6SNvroHX1wP6GQZXGNfgIsFbTPdGcDLr",
                "enableRateLimit": True,

            })




            #기준가격
            for idx,position in enumerate(trade_targets):
                pos=''
                ## 사이즈에 마이너스인지 아닌지를 통해서 long short 구분
                if position['positionAmt'][0]=='-':
                    pos='S'
                else:
                    pos='L'
                levearge=float(position['leverage'])
                symbol=position_symbol(position['symbol']) #symbol name
                pos_price=float(position['entryPrice']) #포지션 가격
                price=float(binance.fetch_ticker(symbol)['last'])  #현재가

                orders =binance.fetchOpenOrders(symbol)
                for order in orders:
                    if order['type']=='stop_market':
                        stop_order=order
                if 'stop_order' in locals():
                    stopprice=float(stop_order['stopPrice'])

                if pos=='S':
                    print(symbol+' Short position')
                    if (1-(0.03/levearge))*pos_price > price:
                        if 'stop_order' in locals():
                            if stopprice>pos_price:
                                binance.cancel_order(stop_order['id'],symbol)
                                binance.create_order(symbol, 'stop_market', side='buy', amount=float(position['positionAmt'][1:]),params={'stopPrice': price * (1 + (0.01 / levearge))})
                        else:
                            binance.create_order(symbol,'stop_market',side='buy',amount=float(position['positionAmt'][1:]),params={ 'stopPrice': price *(1+(0.01/levearge))})


                else:
                    print(symbol + ' Long position')
                    if (1+(0.03 / levearge)) * pos_price < price :
                        if 'stop_order' in locals():
                            if stopprice<pos_price:
                                 binance.cancel_order(stop_order['id'], symbol)
                                 binance.create_order(symbol, 'stop_market', side='sell', amount=float(position['positionAmt']),params={'stopPrice': price * (1 - (0.01 / levearge))})
                        else:
                             binance.create_order(symbol, 'stop_market', side='sell', amount=float(position['positionAmt']),
                                                 params={'stopPrice': price * (1 - (0.01 / levearge))})


#endregion

thread1 = threading.Thread(target=loss_trailing)
thread1.start()
thread1.join()

#thread2 = threading.Thread(target=AUTO_trading)
#thread2.start()
#thread2.join()

