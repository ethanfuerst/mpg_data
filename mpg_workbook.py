# %%
from IPython import get_ipython
import pandas as pd
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
from datetime import date, timedelta, datetime
import urllib.request, json, os, itertools, threading, time, sys
get_ipython().run_line_magic('matplotlib', 'inline')
df_m = pd.read_csv('clean_m_data.csv', index_col = 0, parse_dates = ['date'])
df_m.name = 'Moped Data'
df_c = pd.read_csv('clean_c_data.csv', index_col = 0, parse_dates = ['date'])
df_c.name = 'Car Data'
df_w = pd.read_csv('weather_data.csv', index_col = 0, parse_dates = ['date'])
df_w.name = 'Weather Data'


# %%


