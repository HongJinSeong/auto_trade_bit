# auto_trade_bit

바이낸스 선물 자동거래 프로그램

돈번적없고 다잃음 크게 하면 망할듯?

CCXT 사용해서 개발 

****************** 동작 기준 **************************

 자동매매 ver.1 RSI 기준
 이더리움 비트 제외하고 5분봉 기준 rsi가 75을 넘고 하락 OR 25를 넘고 상승인 경우에 TP 3% SL -3%기준으로 set하고 거래 하도록 진행
 익절 - TP 도달 OR trailing에 의해서 레버리지를 고려한 1%로 익절 진행
 손절 - SL 도달 기준
 한번 포지션을 가져간 종목은 익절이나 손절에 의해 해당 position 종료전까지 거래 X
 레버리지 5배로 set하여 돌리기 ==> 레버리지나 TP SL은 해보면서 log쌓은이후에 조정해보는걸로..
 
 ****************** 동작 기준 **************************
 
 telegram으로 자동알람까지 추가

 선물 자동 프로그램을 개발해봤다는 것 자체에 의의를 둠..
 
 talib ==> 주식이나 코인같은 데이터에 적용하기 좋은 library 많은 함수 지원
 다음에 금융관련 데이터 다룰 일이 있다면 또 사용해봄직함
