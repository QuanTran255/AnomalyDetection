from ProphetVNG import ProphetVNG
import request_vng
import schedule
import time
#import datetime
import pandas as pd
from datetime import datetime, timezone, timedelta
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

yhat = None                 #predicted y
yhat_lower = None           #predicted y lower bound
yhat_upper = None           #predicted y upper bound
y = None                    #actual y


'''
log data
'''
f = open("log.txt", "a")
f.write("#################################\n")
f.close()
f = open("demofile.txt", "a")
f.write("#################################\n")
f.close()


'''
round a datetime value to the nearest minute
'''
def datetime_str(d:datetime):
    strnow = pd.Timestamp(d)._repr_base
    strnow1 = strnow[:strnow.index(" ")]
    strnow2 = strnow[strnow.index(" ")+1:]
    strnow = strnow1+"T"+strnow2
    #strnow = strnow[:strnow.index(".")+4]
    #strnow += "Z"
    strnow = strnow[:strnow.index(".")]
    strnow = strnow[:len(strnow)-3]
    strnow += ":00.000Z"
    
    return strnow

'''
temporary anomaly detection logic

adjust the lower and upper bounds with a threshold specific to the data
    - the bounds from Prophet are too big for hourly trend and too small for daily trend for vund3 data log
    - maybe change the function so that customers can set the threshold for hourly trend (expected value for hourly trend)
      and daily trend would use the bounds as they are given by prophet
'''
def anomaly_detect(now):
    
    threshold = 200
    
    cur_y = y[-1]
    y_est = yhat[0]
    yhat_u = yhat_upper[0]*1.5
    yhat_l = yhat_lower[0]-(yhat_u-yhat_upper[0])
    
    
    if y_est<threshold:
        if not(yhat_l/2<=cur_y and cur_y<=yhat_u/2):
            f = open("demofile.txt", "a")
            f.write(str(now)+"\t"+str(cur_y)+"\n")
            f.close()
        log = (str(round(yhat_l/2,2))+"\t"+
              str(round(y_est,2))+"\t"+
              str(round(cur_y,2))+"\t"+
              str(round(yhat_u/2,2))+"\n")
        f = open("log.txt", "a")
        f.write(log)
        f.close()
        print(log)
    else:
        if not(yhat_l<=cur_y and yhat_u>=cur_y):
            f = open("demofile.txt", "a")
            f.write(str(now)+"\t"+str(y[-1])+"\n")
            f.close()
        log = (str(round(yhat_l,2))+"\t"+
               str(round(y_est,2))+"\t"+
               str(round(cur_y,2))+"\t"+
               str(round(yhat_u,2))+"\n")
        f = open("log.txt", "a")
        f.write(log)
        f.close()
        print(log)

####################################################################
#               Attempt at plotting live data                      #
####################################################################
x_counter = 0
xs = []        
yus = []
ys = [] 
y_act = []   
yls = [] 
fig = plt.figure()
ax = plt.subplot(1,1,1)
#style.use('fivethirtyeight')  
    
def live_data():
    
    global x_counter
    
    cur_y = y[-1]
    y_est = yhat[0]
    yhat_u = yhat_upper[0]
    yhat_l = yhat_lower[0]-(yhat_u-yhat_upper[0])
    
    xs.append(x_counter)
    yus.append(yhat_u)
    ys.append(y_est)
    y_act.append(cur_y)
    yls.append(yhat_l)
    
    x_counter += 1
    
    
    
def plot_live(i):
    
    ax.clear()
    #ax.plot(xs, y_act)
    ax.plot(xs, ys)
    #ax.fill_between(xs, yus, yls, facecolor = 'orange', alpha = 0.3)
    
    #temp = 0
    
####################################################################    

timer = 60*0

def job():
    global timer    
    global yhat_lower
    global yhat_upper
    global yhat
    global y
    
    
    now = datetime.now(timezone.utc)
    d = timedelta(days = 10)        #number of available training days
    d1 = timedelta(minutes = 10)    #same value as the interval used for averaging values (in the presentation, 10 min was shown to have a small error)
    d2 = timedelta(minutes = timer) #absolute shift in training data
    now = now-d2                    #current time of interest
    train = now-d1                  #
    past = train-d                  #
    
    now = datetime_str(now)
    train = datetime_str(train)
    past = datetime_str(past)
    
    if yhat_lower is not None:
        anomaly_detect(now)
        
    
    
    #change curl to get different data
    curl = (
        "https://hcm-3.console.vngcloud.vn/vmonitor/log-api/v1/projects/4fc7d579-c1ac-483d-8a59-f9e61d2a6a73/search-logs"
        )
    curl1 = (
        "https://hcm-3.console.vngcloud.vn/vmonitor/log-api/v1/projects/3384b481-908f-4953-bcdd-a1b710de9663/search-logs")
    url = (
        "https://iamapis.vngcloud.vn/accounts-api/v2/auth/token")
    client_ID = (
        "b1dc61d0-d8ff-4cde-b27b-7ac03c8d996c")
    client_secret = (
        "edae4f39-da45-4bd1-8696-8705de7db883")
    json = {
        "from":0,"size":0,"aggregations":[{"aggregationQuery":{"type":"date_histogram","value":{"name":"aggDate","field":"@timestamp","timeZone":"Asia/Ho_Chi_Minh","calendarInterval":"1m"}},"subAggregation":[{"aggregationQuery":{"type":"value_count","value":{"name":"aggStats","script":"0"}}}]}],"query":{"type":"bool","value":{"filter":[{"type":"range","value":{"field":"@timestamp",
        "gte":"2023-05-10T11:00:51.008Z",
        "lte":"2023-06-20T09:00:51.009Z","format":"strict_date_optional_time"}}],"should":[],"must":[{"type":"bool","value":{"filter":[],"must":[{"type":"exists","value":{"field":"decision_id.keyword"}}],"should":[],"mustNot":[]}}],"mustNot":[]}},"sorts":[{"type":"field_sort","value":{"field":"@timestamp","order":"desc","mode":"min","missing":"_last","unmappedType":"boolean"}}]
                }
    
    
    '''json2 = {
        "from":0,"size":0,"aggregations":[{"aggregationQuery":{"type":"date_histogram","value":{"name":"aggDate","field":"@timestamp","timeZone":"Asia/Ho_Chi_Minh","calendarInterval":"1m"}},"subAggregation":[{"aggregationQuery":{"type":"value_count","value":{"name":"aggStats","script":"0"}}}]}],"query":{"type":"bool","value":{"filter":[{"type":"range","value":{"field":"@timestamp",
        "gte":"2023-05-30T06:37:07.922Z",
        "lte":"2023-06-30T06:37:07.922Z","format":"strict_date_optional_time"}}],"should":[],"must":[{"type":"match_all","value":{}}],"mustNot":[]}},"sorts":[{"type":"field_sort","value":{"field":"@timestamp","order":"desc","mode":"min","missing":"_last","unmappedType":"boolean"}}]}
    '''
    json["query"]['value']['filter'][0]['value']["lte"] = train
    json["query"]['value']['filter'][0]['value']["gte"] = past

    #forecast model which uses data that ends *interval* minutes ago to predict the value 10 min in the future
    vngreq = request_vng.vng(curl, url, client_ID, client_secret, json)

    p = ProphetVNG(vngreq, interval = 10, forecast_days=10, training_days = 6, shift = 0, fourier_order=50)
    p.fit_Prophet()
    
    #p.plot_Prophet()
    r = p.rmse()
    
    #get predicted y values
    yhat = p.predictions.values.tolist()
    yhat_upper = p.predictions_high.values.tolist()
    yhat_lower = p.predictions_low.values.tolist()
    
    #yhat.plot()
    
    #actual value to compare to the predicted value
    json["query"]['value']['filter'][0]['value']["lte"] = now
    vngnow = request_vng.vng(curl, url, client_ID, client_secret, json)
    p_now = ProphetVNG(vngnow, interval = 10, forecast_days=2, training_days = 6, shift = 0, fourier_order=50)
    
    y = p_now.df['y'].values.tolist()       #get actual y value
    

    #r = p.rmse()
    min_rmse = r
    rmse_mat = []
    
    #calculate rmse with various parameter
    if(0):
        for i in range(30,0,-1):
            #break
            t_list = []
            if 1440%i == 0:
                for t in range(3,19,1):
                    
                    avg_rmse = 0
                    counter = 0
                    for s in range(0, 10):
                        hw = ProphetVNG(vngreq, interval = i, forecast_days=2, training_days=t, shift = s, fourier_order = 50)
                        hw.fit_Prophet()
                        avg_rmse += hw.rmse()
                        counter +=1
                        print("i = "+str(i) + " t = " + str(t) + " s = "+str(s))
                        
                    avg_rmse /= counter
                    
                    t_list.append(avg_rmse)
                    
                    min_rmse = min(min_rmse,avg_rmse)
                
                rmse_mat.append(t_list)


job()





schedule.every(55).seconds.do(job)

while True:
    schedule.run_pending()
    #time.sleep(1)
    
ani = animation.FuncAnimation(fig, plot_live, interval=1000)
plt.show()

