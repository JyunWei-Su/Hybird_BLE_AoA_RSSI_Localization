from re import T
import secrets
import sys
# from tokenize import group
# from django import conf
import psycopg2
import warnings ## bypass psycopg2 connection warning
from config import config
import pandas as pd
import numpy as np
from numpy import linalg as la
import pprint as pp
import socket
import json
import os 
import csv
import math

import scipy.stats as stats # for 相關度分析

# Listen for incoming datagrams
    
import configparser
from datetime import datetime
# @see usage: https://www.delftstack.com/zh-tw/howto/python/python-ini-file/

#-------
from turtle import color
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
import matplotlib.patches as patches

# get the anchor config from config file
def get_system_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    config_dict = config._sections
    for instance in [section for section in config.sections() if 'anchor' in section or 'tag' in section]:
        for key in config_dict[instance].keys():
            config_dict[instance][key] = eval(config_dict[instance][key])
    return config_dict

def get_measurement_data(start_time_ms:int, duration_ms:int): # time format in ms
    conn = None
    cur = None
    df = None
    try:
        with warnings.catch_warnings():
            # ignore warning for non-SQLAlchemy Connecton
            # see github.com/pandas-dev/pandas/issues/45660
            warnings.simplefilter('ignore', UserWarning)
            # read database configuration
            params = config()
            # connect to the PostgreSQL database
            conn = psycopg2.connect(**params)
            conn.autocommit = True
            # create a new cursor
            cur = conn.cursor()
            df = pd.read_sql_query(f"SELECT unix_time, anchor_id, instance_id, azimuth \
                    FROM measurement WHERE unix_time BETWEEN {start_time_ms} AND {start_time_ms+duration_ms}",con = conn)
            cur.close()
            if conn is not None:
                conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return df

#========================================================================
start_time = 1668672951000
start_time = 1668673044000
start_time = 1668673215000
start_time = 1668673311000
start_time = 1668673417000
start_time = 1668673579000
anchor_list = ['anchor-a', 'anchor-b']
tag_list = ['tag-a']
move_avg_count = 2


system_config = get_system_config("system.ini")
print('config get')
df = get_measurement_data(start_time, 60000)


df['time'] = pd.to_datetime(df['unix_time'], unit='ms', utc=True).dt.strftime('%Y-%m-%d %H:%M:%S.%f')
df['time'] = df['time'].apply(pd.Timestamp)


dfs = []

for anchor in anchor_list:
    anchor_type = system_config[anchor]['type']
    anchor_id = system_config[anchor]['id']
    if anchor_type == 'rssi+aoa:xplr-aoa':
        for tag in tag_list:
            mask_anchor = (df['anchor_id'] == anchor_id)
            mask_tag = (df['instance_id'] == system_config[tag]['id'])
            temp = df[(mask_anchor & mask_tag)]
            temp = temp.resample('0.5S', on='time').mean() ##dddd
            temp = temp.drop(columns=[ 'unix_time'])
            temp['anchor'] = [anchor + '@chmix'] * len(temp)
            #temp['tag'] = [tag + '@' + str(system_config[tag]['tx_power'])] * len(temp)
            #print(temp)
            dfs.append(temp)

measurement_data = pd.concat(dfs)
measurement_data = measurement_data.reset_index()
print(measurement_data)
#os.system("pause")

times = measurement_data['time']
times = times.drop_duplicates()
times = times.sort_values()
#print(times)
#print(measurement_data)
print('data_get')

# Python program to get average of a list
def avg(lst):
    return sum(lst) / len(lst)

def cal_loc(system_config:dict, df:pd.DataFrame):
    angle_a = []
    angle_b = []
    for index in df.index: #   time    rssi  azimuth  elevation  anchor  tag
        anchor = df['anchor'][index]
        anchor_name = anchor.split('@')[0]
        if anchor_name == 'anchor-a':
            angle_a.append(90 + df['azimuth'][index])
        elif anchor_name == 'anchor-b':
            angle_b.append(90- df['azimuth'][index])
    angle_a = avg(angle_a)
    angle_b = avg(angle_b)
    # print("ANGLE", angle_a, angle_b)
    angle_apb = angle_a + angle_b
    angle_a = angle_a / 360 * (2*math.pi)
    angle_b = angle_b / 360 * (2*math.pi)
    angle_apb = angle_apb / 360 * (2*math.pi)
    d = 12.5 * math.sin(angle_a) * math.sin(angle_b) / math.sin(angle_apb)
    u = d / math.tan(angle_b)
    return (u, d)



print(times.index)
xy_list = []
for time_index in times.index:
    if time_index >= len(times.index) - move_avg_count:
        break
    frams = []
    time = times[time_index]
    frams.append(measurement_data[measurement_data['time'] == time])
    for i in range(1, move_avg_count):
        frams.append(measurement_data[measurement_data['time'] == times[time_index + i]])
    data_on_time  = pd.concat(frams)
    print(time)
    #print(data_on_time)
    try:
        location = cal_loc(system_config, data_on_time)
        #os.system('pause')
        (x, y) = (float(location[0]), float(location[1]))
        #print(time.strftime('%Y-%m-%d %H:%M:%S.%f'), x, y)
        if(not np.isnan(x) and not np.isnan(y)):
            xy_list.append((x, y))
    except:
        print('', end='')
print(xy_list)
xy_df = pd.DataFrame(xy_list)
print(xy_df)
std_x = xy_df[0].std()
std_y = xy_df[1].std()
print('std_x:', std_x)
print('std_y:', std_y)
# xy_df.to_csv('T1.csv')
r, p = stats.pearsonr(xy_df[0], xy_df[1])  # 相關係數r和p值
print('相關係數r^2 = %6.3f, p = %6.3f' % (r * r, p))


#-------------------------

fig, ax = plt.subplots()
ax.set_ylim(-1, 13.5)
ax.set_xlim(-1, 13.5)
# Change major ticks to show every 20.
ax.xaxis.set_major_locator(MultipleLocator(6))
ax.yaxis.set_major_locator(MultipleLocator(6)) # 主要格線距離

# Change minor ticks to show every 5. (20/4 = 5)
ax.xaxis.set_minor_locator(AutoMinorLocator(12))
ax.yaxis.set_minor_locator(AutoMinorLocator(12)) # 切n段

# Turn grid on for both major and minor ticks and style minor slightly
# differently.
ax.grid(which='major', color='#CCCCCC', linestyle='dashed')
ax.grid(which='minor', color='#CCCCCC', linestyle='dotted')

tiles = []
for x in range(0, 25):
    for y in range(0, 37):
        if x % 6 == 0 and y % 6 == 0:
            tiles.append((x/2, y/2))
        elif (x-3) % 6 == 0 and (y-3) % 6 == 0:
            tiles.append((x/2, y/2))
for tile in tiles:
    rect = patches.Rectangle(tile, 0.5, 0.5, linewidth=1, edgecolor='none', facecolor='mistyrose')
    ax.add_patch(rect)
#                         x  y   w  h

# Add the patch to the Axes

def plot_anchor(x, y, nickName, type):
    if(type == 'xplr-aoa'):
        plt.scatter(x, y, marker='^', color='limegreen', s=75) #xplr-aoa
        ax.text(x, y-0.5, 'xplr-aoa', fontsize=8, horizontalalignment='center', verticalalignment='center', color='limegreen')
        ax.text(x, y+0.5, nickName, fontsize=8, horizontalalignment='center', verticalalignment='center', color='limegreen')
    elif(type == 'esp32'):
        plt.scatter(x, y, marker='v', color='deepskyblue', s=75) #esp32
        ax.text(x, y-0.5, 'esp32', fontsize=8, horizontalalignment='center', verticalalignment='center', color='deepskyblue')
        ax.text(x, y+0.5, nickName, fontsize=8, horizontalalignment='center', verticalalignment='center', color='deepskyblue')

def plot_tag(x, y, tagName):
    plt.scatter(x, y, marker='o', color='red', s=75)
    ax.text( x, y+0.5, tagName, fontsize=8, horizontalalignment='center', verticalalignment='center', color='red')

plot_anchor(   0,    0, 'Anchor B', 'xplr-aoa')
plot_anchor(12.5,    0, 'Anchor A', 'xplr-aoa')
plot_anchor(   0, 12.5, 'Anchor D', 'esp32')
plot_anchor(12.5, 12.5, 'Anchor C', 'esp32')

plot_tag(9.25, 3.25, 'T1')
#plot_tag(6.25, 3.25, 'T2')
plot_tag(3.25, 3.25, 'T2')
plot_tag(3.25, 9.25, 'T3')
plot_tag(9.25, 9.25, 'T4')
plot_tag(6.25, 6.25, 'T5')

# 作圖,marker:散點圖形裝,label設定圖例
plt.scatter(-1, -1, color='white', marker='.', label='r^2 = %6.3f'%(r*r))
plt.scatter(-1, -1, color='white', marker='.', label='std_x = %6.3f'%(std_x))
plt.scatter(-1, -1, color='white', marker='.', label='std_y = %6.3f'%(std_y))
# 設定圖例位置
plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="center left", mode="expand", borderaxespad=0, ncol=3)
#plt.legend(loc=(1.04, 0))

for point_x, point_y in xy_list:
    plt.scatter(point_x, point_y, marker='.', color='blue', s=10)

plt.scatter(6.25, 6.25, marker='x', color='yellow', s=75) #tag r

plt.title("T5 mov_avg="+ str(move_avg_count) + '')

plt.show()