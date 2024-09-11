# 載入必要套件
import pandas as pd
from Data import getData
from BackTest import ChartTrade, Performance
import mplfinance as mpf
from talib.abstract import SMA

# 取得回測資料
prod = '0050'
data = getData(prod, '2013-01-01', '2022-05-01')

# 計算簡單移動平均線
data['ma1'] = SMA(data, timeperiod=90)
data['ma2'] = SMA(data, timeperiod=120)
data['ma3'] = SMA(data, timeperiod=150)

# 初始部位
position = 0
trade = pd.DataFrame()
# 開始回測
for i in range(data.shape[0]-1):
    # 取得策略會應用到的變數
    c_time = data.index[i]
    c_high = data.loc[c_time, 'high']
    c_close = data.loc[c_time, 'close']
    c_ma1 = data.loc[c_time, 'ma1']
    c_ma2 = data.loc[c_time, 'ma2']
    c_ma3 = data.loc[c_time, 'ma3']
    c_macd = data.loc[c_time,'open']
    # 取下一期資料做為進場資料
    n_time = data.index[i+1]
    n_open = data.loc[n_time, 'open']

    # 進場程序
    if position == 0:
        # 進場邏輯
        if c_ma1 > c_ma2 > c_ma3 and c_macd>5:
            position = 1
            order_i = i
            order_time = n_time
            order_price = n_open
            order_unit = 1
    # 出場程序
    elif position == 1:
        # 出場邏輯
        if (not c_ma1 > c_ma2 > c_ma3) :
            position = 0
            cover_time = n_time
            cover_price = n_open
            # 交易紀錄
            trade = pd.concat([trade, pd.DataFrame([[
                prod, 
                'Buy', 
                order_time, 
                order_price, 
                cover_time, 
                cover_price, 
                order_unit
            ]])], ignore_index=True)

# 繪製副圖
addp = []
addp.append(mpf.make_addplot(data['ma1']))
addp.append(mpf.make_addplot(data['ma2']))
addp.append(mpf.make_addplot(data['ma3']))

# 績效分析
Performance(trade, 'ETF')
# 繪製K線圖與交易明細
ChartTrade(data, trade, addp=addp)
