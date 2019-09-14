import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import datetime as dt
from datetime import date, timedelta, datetime
import urllib.request, json, os, itertools, threading, time, sys

print("Please do not close the window.")
print("mpg_extract.py will print how long it took to run when it is completed.")
done = False
# a nice animation while the program is running
def animate():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\rmpg_extract.py is running ' + c)
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\n')

t = threading.Thread(target=animate)
t.start()

# lets see how long this takes
startTime = datetime.now()

'''
First I will pull the data from moped_mpg_data.csv and car_mpg_data.csv
and save them as clean_c_data.csv and clean_m_date.csv
'''

df_m = pd.read_csv('moped_mpg_data.csv')
df_m.name = 'Moped Data'
df_c = pd.read_csv('car_mpg_data.csv')
df_c.name = 'Car Data'

# creating new column for how much a gallon of gas cost for each entry
for i in [df_m, df_c]:
    i['gal_cost'] = i.dollars / i.gallons
    i['mpg'] = i.miles / i.gallons

# creating a new column to determine what percent of my tank was used up when filled up
# moped tank size = 1.37 gallons
df_m['tank%_used'] = df_m['gallons'] / 1.37
# car tank size = 13.55 gallons
df_c['tank%_used'] = df_c['gallons'] / 13.55

# following method used in for loop
def as_day(i):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return days[i]

for i in [df_m, df_c]:
    # changes column to datetime
    i['date'] = pd.to_datetime(i['date'])

    # creates column with day of the week
    i['day'] = i['date'].dt.dayofweek
    i['day'] = i['day'].apply(as_day)

    # creates a new column that records the number of days since the last fillup
    i['days_since_last_fillup'] = i['date'].diff().dt.days

# creates unique id in the form vehicle-date-index of vechicle df
df_c = df_c.assign(id=('c' + '-' + df_c['date'].dt.strftime("%d-%b-%Y") + "-" + df_c.index.map(str)))
df_m = df_m.assign(id=('m' + '-' + df_m['date'].dt.strftime("%d-%b-%Y") + "-" + df_m.index.map(str)))

# creates clean_c_data.csv and clean_m_data.csv
df_c.to_csv('clean_c_data.csv')
df_m.to_csv('clean_m_data.csv')

'''
Now to get the weather data from https://darksky.net/
'''

# https://darksky.net/dev/docs requests I keep my key hidden
# Going back a directory to access darkskyid.txt and save as my_id
os.chdir("..")
my_id = open('darkskyid.txt', 'r').read()
# Going back to original directory
os.chdir("/Users/ethanfuerst/Documents/Coding/mpgdata")

# creating a range of dates to get - shoutout date.today()
# I'm using a moving average of 3, so doing this I will have data Jan 1 2019
sdate = date(2018, 12, 30)   # start date - Dec 30 2018
edate = date.today()       # today

delta = edate - sdate       # as timedelta

# creating a list for each day in the range
# using unix time because that's what the darksky api uses
# each date will give me the unix time at 6pm for that day
# the daily_high and daily_low are the parameters that I will use to see how my mpg changes
date_list = []
for i in range(1, delta.days + 1):
    day = sdate + timedelta(days=i)
    date_list.append(int((day - dt.date(1970,1,1)).total_seconds()))

# creating a list for each api call
api_list = []
for i in date_list:
    api_list.append('https://api.darksky.net/forecast/'+my_id+'/30.267153,-97.7430608,'+str(i)+'?exclude=flags,hourly')

# getting the high temp and low temp for each day
date = []
daily_high = []
daily_low = []
for api in api_list:
    with urllib.request.urlopen(api) as url:
        data = json.loads(url.read().decode())
        # keeping day in yyyymmdd format, just like in other dataframes
        date.append(datetime.fromtimestamp(data["currently"]["time"]).strftime("20%y/%m/%d"))
        daily_high.append(data["daily"]["data"][0]["temperatureHigh"])
        daily_low.append(data["daily"]["data"][0]["temperatureLow"])

# putting all the lists in to a dateframe
df_weather = pd.DataFrame({'date': date, 'daily_high': daily_high, 'daily_low': daily_low})
df_weather['high_mov_avg'] = df_weather['daily_high'].rolling(window=3).mean()
df_weather['low_mov_avg'] = df_weather['daily_low'].rolling(window=3).mean()

# need to drop the records in 2018 that I used for the moving average
df_weather.drop([0,1], inplace=True)
# and then reset the index
df_weather.reset_index(drop=True)

# and finally ... saving the df_weather to a .csv
df_weather.to_csv('weather_data.csv')

# stop the animation and print the time
minutes, seconds = divmod((datetime.now() - startTime).seconds,60)
print("mpg_extract.py ran in {} minutes and {} seconds".format(minutes,seconds))

done = True