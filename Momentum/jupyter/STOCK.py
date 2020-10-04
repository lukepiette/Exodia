#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pyEX as p
import datetime
import os
import json


# In[2]:


class Stock(object):
    
    def __init__(self):
        self.secret = 'sk_fae174660924464996b77d14209a973b'
        self.public = 'pk_2f3691af11ad4df583c95f2a4d89d44a'
        p.Client(api_token=self.secret, version='v1', api_limit=5)
    
    
    def get6Months(self,ticker):
        # 1 day
        history = p.chart(symbol=ticker, timeframe='6m', date=None, token=self.secret, version='v1', filter='')        
        PATH = f'./stock/6m/{ticker}.json'
        
        data = {}
        for chunk in history:
            formatted = {}
            formatted['open'] = chunk['open']
            formatted['close'] = chunk['close']
            formatted['high'] = chunk['high']
            formatted['low'] = chunk['low']
            formatted['volume'] = chunk['volume']
            
            data[chunk['date']] = formatted

        with open(PATH,'w') as JSON:
            json.dump(data,JSON)
            
        print('Done 6m.')
        
    
    def get5Days(self,ticker):
        # 10 min
        history = p.chart(ticker, timeframe='5dm', date=None, token=self.secret, version='v1', filter='')        
        PATH = f'./stock/5d/{ticker}.json'
        
        data = {}
        for chunk in history:
            formatted = {}
            formatted['price'] = chunk['average']
            formatted['volume'] = chunk['volume']

            date = chunk['date']
            try:
                data[date][chunk['minute']] = formatted
            except:
                data[date] = {chunk['minute']:formatted}
            
        with open(PATH,'w') as JSON:
            json.dump(data,JSON)
            
        print('Done 5d.')
    


    def pushToEMA(self,ticker,timestamp,date):
        if timestamp == '16:00:00':
            PATH_LIVE = f'./stock/1d/{ticker}.json'
            PATH_6M = f'./stock/6m/{ticker}.json'
            PATH_5D = f'./stock/5d/{ticker}.json'

            oldData6M = {}
            oldData5D = {}

            with open(PATH_LIVE,'r') as JSON:
                todayData = json.load(JSON)
            with open(PATH_6M,'r') as JSON:
                fiveDayData = json.load(JSON)
            with open(PATH_5D,'r') as JSON:
                sixMonthData = json.load(JSON)

            for DATE in todayData:
                formatted = {}
                for chunk in todayData[DATE]:
                    price = chunk['price']
                    volume = chunk['volumeDelta']

                    tim = int(chunk[3:5])
                    if tim < 10:
                        tim = '00'
                    elif tim < 20:
                        tim = '10'
                    elif tim < 30:
                        tim = '20'
                    elif tim < 40:
                        tim = '30'
                    elif tim < 50:
                        tim = '40'
                    elif tim < 60:
                        tim = '50'

                    formatted[chunk[0:3]+tim] = {'price':price,'volume':volume}
                oldData5D[DATE] = formatted

                oldData = p.quote(symbol=ticker, token=self.secret, version='v1')
                open_ = oldData['open']
                close_ = oldData['close']
                high_ = oldData['high']
                low_ = oldData['low']
                volume_ = oldData['volume']
                
                oldData6M[DATE] = {'open':open_,'close':close_,'high':high_,'low':low_,'volume':volume_}

 
            with open(PATH_6M,'w') as JSON:
                json.dump(oldData6M,JSON)
            with open(PATH_5D,'w') as JSON:
                json.dump(oldData5D,JSON)


    def getLiveQuote(self,ticker):
        # Snapshot
        today = p.quote(symbol=ticker, token=self.secret, version='v1')
        PATH = f'./stock/1d/{ticker}.json'
        
        old_data = {}
        if os.path.exists(PATH):
            with open(PATH,'r') as JSON:
                old_data = json.load(JSON)

        date = int(str(today['latestUpdate'])[0:-3])
        dateYYMMDD = str(datetime.datetime.fromtimestamp(date)).split(' ')[0]
        timestamp = str(datetime.datetime.fromtimestamp(date)).split(' ')[1]    
        
        formatted = {}
        formatted['price'] = today['iexRealtimePrice']
        formatted['volume'] = today['volume']
        
        try:
            volumeDelta = today['volume'] - old_data['lastVolume']
            formatted['volumeDelta'] = volumeDelta
        except:
            formatted['volumeDelta'] = 0
            
        old_data['lastVolume'] = today['volume']
        try:
            old_data[dateYYMMDD][timestamp] = formatted
        except:
            old_data[dateYYMMDD] = {timestamp:formatted}
        
        with open(PATH,'w') as JSON:
            json.dump(old_data,JSON)

        self.pushToEMA(ticker,timestamp,dateYYMMDD)
        print('Done Live.')
    
    
    def run(self,ticker):
        PATH_6M = f'./stock/6m/{ticker}.json'
        PATH_5D = f'./stock/5d/{ticker}.json'
        PATH_1D = f'./stock/1d/{ticker}.json'
        
        if os.path.exists(PATH_6M) != True:
            self.get6Months(ticker)
        if os.path.exists(PATH_5D) != True:
            self.get5Days(ticker)
            
        self.getLiveQuote(ticker)


# In[ ]:


#c = Stock()
#c.run('HEXO')

