import pandas as pd
from Data import getData
from BackTest import ChartTrade, Performance
import mplfinance as mpf
from talib.abstract import SMA, MACD

# 取得回測資料
prod = '0050'
data = getData(prod, '2013-01-01', '2022-05-01')

# 計算簡單移動平均線
data['ma1'] = SMA(data, timeperiod=90)
data['ma2'] = SMA(data, timeperiod=120)
data['ma3'] = SMA(data, timeperiod=150)

# 計算 MACD 指標
macd, macd_signal, macd_hist = MACD(data, fastperiod=12, slowperiod=26, signalperiod=9)
data['macd'] = macd
data['macd_signal'] = macd_signal

# 初始部位
position = 0
trade = pd.DataFrame()
order_price = None
order_time = None

# 交易策略參數
stop_loss_pct = 0.03  # 止損百分比
take_profit_pct = 0.05  # 止盈百分比

# 開始回測
for i in range(data.shape[0]-1):
    # 取得策略會應用到的變數
    c_time = data.index[i]
    c_high = data.loc[c_time, 'high']
    c_close = data.loc[c_time, 'close']
    c_ma1 = data.loc[c_time, 'ma1']
    c_ma2 = data.loc[c_time, 'ma2']
    c_ma3 = data.loc[c_time, 'ma3']
    c_macd = data.loc[c_time, 'macd']
    c_macd_signal = data.loc[c_time, 'macd_signal']
    
    # 取下一期資料做為進場資料
    n_time = data.index[i+1]
    n_open = data.loc[n_time, 'open']
    
    # 進場條件：MA金叉且MACD大於MACD信號線
    if position == 0 and c_ma1 > c_ma2 > c_ma3 and c_macd > c_macd_signal:
        position = 1
        order_price = n_open
        order_time = n_time
        print(f"進場：{n_time}, 價格：{n_open}")

    # 出場條件：收盤價低於MA或者達到止損/止盈
    elif position == 1:
        stop_loss_price = order_price * (1 - stop_loss_pct)
        take_profit_price = order_price * (1 + take_profit_pct)
        
        if n_open <= stop_loss_price or n_open >= take_profit_price:
            position = 0
            trade = pd.concat([trade, pd.DataFrame([[
                prod, 
                'Buy', 
                order_time, 
                order_price, 
                n_time, 
                n_open, 
                1
            ]])], ignore_index=True)
            print(f"出場：{n_time}, 價格：{n_open}, 原因：止損/止盈")

        elif not (c_ma1 > c_ma2 > c_ma3):
            position = 0
            trade = pd.concat([trade, pd.DataFrame([[
                prod, 
                'Buy', 
                order_time, 
                order_price, 
                n_time, 
                n_open, 
                1
            ]])], ignore_index=True)
            print(f"出場：{n_time}, 價格：{n_open}, 原因：MA死叉")

# 繪製副圖
addp = []
addp.append(mpf.make_addplot(data['ma1'], color='blue'))
addp.append(mpf.make_addplot(data['ma2'], color='orange'))
addp.append(mpf.make_addplot(data['ma3'], color='green'))
addp.append(mpf.make_addplot(data['macd'], panel=1, color='red'))
addp.append(mpf.make_addplot(data['macd_signal'], panel=1, color='blue'))

# 績效分析
Performance(trade, 'ETF')
# 繪製K線圖與交易明細
ChartTrade(data, trade, addp=addp)
