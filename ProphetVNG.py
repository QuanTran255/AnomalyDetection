# dataframe opertations - pandas
import pandas as pd
# plotting data - matplotlib
from matplotlib import pyplot as plt
# time series - Prophet 
from prophet import Prophet

import math

import request_vng

class ProphetVNG:
    
    data = None
    interval = 1
    forecast_days = 0
    training_days = 7
    shift = 0
    df = None
    fourier_order = 0
    confidence_interval = 0
    
    
    
    train_data = None
    test_data = None
    predictions = None
    predictions_high = None
    predictions_low = None
    forecast = None
    
    
    def __init__(self, vngreq:request_vng, interval:int, forecast_days = 2, training_days = 7, shift = 0, fourier_order = 10, confidence_interval = 0.99):
        
        response = vngreq.post_data()
        self.data = response["aggregations"]["aggDate"]["buckets"]
        self.interval = interval
        self.forecast_days = forecast_days
        self.training_days = training_days
        self.shift = shift
        self.fourier_order = fourier_order
        self.confidence_interval = confidence_interval
        self.df = self.json_to_df(self.data)
    
    
    ################################
    #   Get values and dates from  #
    #           json body          #
    ################################
    def json_to_df(self, data):
        
        date = []
        val = []
        
        
        for i in range(0, len(data), self.interval):
            d = data[i]["key_as_string"]
            d = str(d).replace("T", " ")
            d = d[:d.index(".")]
            d = d[:len(d)-3]
            
            #calculate average value
            avgval = 0
            counter = 0
            
            for c in range(self.interval):
                if i+c<len(data):
                    value = data[i+c]["doc_count"]
                    avgval+=value
                    counter +=1
            avgval/=counter
            val.append(avgval)
            date.append(d)
        
        df = pd.DataFrame({
            "ds": date,
            "y": val
        })
       
        return df
    
    
    def set_shifts(self, days:int):
        self.shift = days
    
    def set_interval(self, interval:int):
        self.interval = interval
        
    def fit_Prophet(self):
        
        if 1440%self.interval != 0:
            return
        
        #splitting up the data according to the number of training days and forecast days
        dataLen = len(self.df['y'])
        splitData = int(dataLen-(self.forecast_days+self.shift)*1440/self.interval)
        train_start_ind = round(dataLen-(self.forecast_days+self.training_days+self.shift)*1440/self.interval)
        test_end_ind = int(dataLen-(self.shift)*1440/self.interval)
        self.train_data = self.df[train_start_ind:splitData]
        self.test_data = self.df[splitData:test_end_ind]
        
        #Initializing Prophet object
        m = Prophet(weekly_seasonality=True, interval_width=0.99)
        m.add_seasonality(name = "minute", period=1, fourier_order=self.fourier_order)
        m.fit(self.train_data)
        future = m.make_future_dataframe(periods=int(1440/self.interval*self.forecast_days), freq = str(self.interval)+'min')
        forecast = m.predict(future)
        self.forecast = forecast
        
        #m.plot_components(forecast)
        
        #get upper and lower bound of the forecast
        self.predictions = forecast['yhat']
        self.predictions_high = forecast['yhat_upper']
        self.predictions_low = forecast['yhat_lower']
        
        self.predictions.index+=self.train_data.first_valid_index()
        self.predictions_high.index+=self.train_data.first_valid_index()
        self.predictions_low.index+=self.train_data.first_valid_index()
        
        forecast_ind = int(len(self.predictions)-1440/self.interval*self.forecast_days)
        
        self.predictions = self.predictions[forecast_ind:]
        self.predictions_high = self.predictions_high[forecast_ind:]
        self.predictions_low = self.predictions_low[forecast_ind:]
        
        #self.calc_bounds()
    
    def plot_Prophet(self,figsize=(16,8)): 
        
        ########## NOT WORKING RN ##########
        
        #set up plot
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_title(str(self.interval)+ " minutes, " + str(self.training_days) + " training days")
        plt.xticks(rotation = 90)
        num_plotsticks = (self.training_days+self.forecast_days)*4
        ax.xaxis.set_major_locator(plt.MaxNLocator(num_plotsticks))
        
        #plot [1152-288:]
        forecast_ind = int(len(self.forecast['ds'])-self.forecast_days*1440/self.interval)
        
        dates = self.forecast['ds'][forecast_ind:]
        
        temp = []
        
        for item in dates:
            temp.append(item)
        
        d1 = self.train_data['ds']
        
        if(0):
            ax.fill_between(dates, self.predictions_high.values, self.predictions_low.values, facecolor = 'orange', alpha = 0.3)
            ax.plot(dates, self.test_data['y'], label = 'TEST')
            ax.plot(dates, self.predictions)
        else:
            ax.plot(self.train_data['ds'], self.train_data['y'])
        
        

    ##################################
    #   Calculate RMSE between yhat  #
    #           and actual y         #
    ##################################
    def rmse(self):
        
        
        
        if 1440%self.interval != 0:
            return float("inf")
        first_index_a = self.test_data.first_valid_index()
        first_index_p = self.predictions.first_valid_index()
        sum = 0.0
        for ind in range(len(self.test_data)):
            min_cur_err = (self.test_data['y'][ind+first_index_a]-self.predictions[ind+first_index_p])
            
            flexibility = 0
            
            for c in range(-flexibility,flexibility,1):
                if ind-c>=0 and ind-c<len(self.test_data):
                    min_cur_err = min(abs(self.test_data[ind+first_index_a]-self.predictions[ind+first_index_p-c]), min_cur_err)
            
            sum+=pow(min_cur_err,2)
        sum = sum/len(self.test_data)
        
        return math.sqrt(sum)
    
    
    ########## NOT GOOD ENOUGH RESULTS ##########
    def calc_bounds(self):
        zscore = 2.575829
        sd = self.sd()
        self.predictions_high = []
        self.predictions_low = []
        
        for yhat in self.predictions:
            y_up = yhat + zscore*sd
            y_low = yhat - zscore*sd
            self.predictions_high.append(y_up)
            self.predictions_low.append(y_low)
        
        
    ###############################
    #   Calculate average value   #
    #     of all data points      # 
    ###############################      
    def mean(self):
        train_val = self.train_data['y'].values
        avg = 0
        for val in train_val:
            avg+= val
        avg/= len(train_val)
        return avg
    
    def sd(self):
        mean_val = self.mean()
        y_est = self.predictions.values
        sum = 0
        
        for y in y_est:
            sum += abs(y-mean_val)**2
            
        sum /= len(y_est)
        sd = math.sqrt(sum)
        
        return sd
    
    
        
    