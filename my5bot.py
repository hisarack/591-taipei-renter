from bs4 import BeautifulSoup
import pandas as pd
import requests
import json
import time
import datetime

import configparser
from linebot import LineBotApi
from linebot.models import TextSendMessage


config = configparser.ConfigParser()
config.read('config.ini')
bot_token = config['line']['token']
target_id = config['line']['target_id']

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
url = "https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=0&searchtype=4&mrtline=232&region=1&mrt=1&mrtcoods=66261&pattern=2"
res = requests.get(url, headers=headers)
data = json.loads(res.text)
total = int(data['records'])
df = pd.DataFrame()
for first_index in range(0, total, 30):
    paged_url = "{}&firstRow={}&totalRows={}".format(url, first_index, total)
    res = requests.get(url, headers=headers)
    data = json.loads(res.text)
    temp_df = pd.DataFrame(data['data']['data'])
    df = df.append(temp_df, ignore_index=True)
    df.drop_duplicates(subset=['id'], inplace=True)
    df = df[['id', 'user_id', 'address', 'updatetime', 'price', 'distance']]
    dt = datetime.datetime.now() - datetime.timedelta(hours=1)
    ts = int(time.mktime(dt.timetuple()))
msg = df[df['updatetime'] > ts].to_string(columns=['address', 'price'])

bot = LineBotApi(bot_token)
bot.push_message(target_id, TextSendMessage(text=msg))
