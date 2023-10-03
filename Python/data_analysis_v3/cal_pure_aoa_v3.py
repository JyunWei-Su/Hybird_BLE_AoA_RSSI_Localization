from asyncio.windows_events import NULL
from email.headerregistry import ContentTransferEncodingHeader
from lib2to3.pgen2.pgen import DFAState
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

import random

def circle_diverge(coo:list,R,num:int):
    x_total = 0
    y_total = 0
    points = []
    n = len(coo)
    for (x,y) in coo:
        x_total = x_total + x
        y_total = y_total + y
    (x_avg,y_avg) = ( x_total / n , y_total / n)
    for i in range(0,num):
        theta = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, R)
        x = x_avg + r * math.cos(theta)
        y = y_avg + r * math.sin(theta)
        points.append((x,y))
    return points
    
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

# Python program to get average of a list
def avg(lst):
    return sum(lst) / len(lst)

class position:
    def __init__(self):
        self.init_plt()
        # pass
    
    def set_system_config(self, filename:str):
        config_file = configparser.ConfigParser()
        config_file.read(filename)
        config_dict = config_file._sections
        for instance in [section for section in config_file.sections() if 'anchor' in section or 'tag' in section]:
            for key in config_dict[instance].keys():
                config_dict[instance][key] = eval(config_dict[instance][key])
        self.config = config_dict

    def get_measurement_data(self, start_time_ms:int, duration_ms:int): # time format in ms
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
                df = pd.read_sql_query(f"SELECT unix_time, anchor_id, instance_id, rssi, azimuth, elevation, channel \
                        FROM measurement WHERE unix_time BETWEEN {start_time_ms} AND {start_time_ms+duration_ms}",con = conn)
                cur.close()
                if conn is not None:
                    conn.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        df['time'] = pd.to_datetime(df['unix_time'], unit='ms', utc=False).dt.strftime('%Y-%m-%d %H:%M:%S.%f')
        df['time'] = df['time'].apply(pd.Timestamp)
        self.raw_data = df

    def set_anchor(self, anchor_list:list):
        self.anchor_list = []
        for (anchor_name, channel) in anchor_list:
            if anchor_name in self.config.keys() and channel in self.config[anchor_name]['channel']:
                self.anchor_list.append((anchor_name, channel))
        print(self.anchor_list)
    
    def set_tag(self, tag_name:str):
        self.tag = tag_name
    
    # def resample(self, time:int):
    #     temp = temp.resample('0.5S', on='time').mean() ##dddd

    def pre_process():
        pass
    
    def init_plt(self):
        self.pltmap = pltmap()
        
        self.pltmap.set_anchor(   0,    0, 'Anchor B', 'xplr-aoa')
        self.pltmap.set_anchor(12.5,    0, 'Anchor A', 'xplr-aoa')
        self.pltmap.set_anchor(   0, 12.5, 'Anchor D', 'esp32')
        self.pltmap.set_anchor(12.5, 12.5, 'Anchor C', 'esp32')

        self.pltmap.set_tag(9.25, 3.25, 'T1')
        self.pltmap.set_tag(3.25, 3.25, 'T2')
        self.pltmap.set_tag(3.25, 9.25, 'T3')
        self.pltmap.set_tag(9.25, 9.25, 'T4')
        self.pltmap.set_tag(6.25, 6.25, 'T5')

    

class pltmap:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.ax.set_ylim(-1, 13.5)
        self.ax.set_xlim(-1, 13.5)
        # Change major ticks to show every 20.
        self.ax.xaxis.set_major_locator(MultipleLocator(6))
        self.ax.yaxis.set_major_locator(MultipleLocator(6)) # 主要格線距離

        # Change minor ticks to show every 5. (20/4 = 5)
        self.ax.xaxis.set_minor_locator(AutoMinorLocator(12))
        self.ax.yaxis.set_minor_locator(AutoMinorLocator(12)) # 切n段

        # Turn grid on for both major and minor ticks and style minor slightly
        # differently.
        self.ax.grid(which='major', color='#CCCCCC', linestyle='dashed')
        self.ax.grid(which='minor', color='#CCCCCC', linestyle='dotted')

        tiles = []
        for x in range(0, 25):
            for y in range(0, 37):
                if x % 6 == 0 and y % 6 == 0:
                    tiles.append((x/2, y/2))
                elif (x-3) % 6 == 0 and (y-3) % 6 == 0:
                    tiles.append((x/2, y/2))
        for tile in tiles:
            rect = patches.Rectangle(tile, 0.5, 0.5, linewidth=1, edgecolor='none', facecolor='mistyrose')
            self.ax.add_patch(rect)
        #                         x  y   w  h
    def set_anchor(self, x, y, nickName, type):
        if(type == 'xplr-aoa'):
            self.ax.scatter(x, y, marker='^', color='limegreen', s=75) #xplr-aoa
            self.ax.text(x, y-0.5, 'xplr-aoa', fontsize=8, horizontalalignment='center', verticalalignment='center', color='limegreen')
            self.ax.text(x, y+0.5, nickName, fontsize=8, horizontalalignment='center', verticalalignment='center', color='limegreen')
        elif(type == 'esp32'):
            self.ax.scatter(x, y, marker='v', color='deepskyblue', s=75) #esp32
            self.ax.text(x, y-0.5, 'esp32', fontsize=8, horizontalalignment='center', verticalalignment='center', color='deepskyblue')
            self.ax.text(x, y+0.5, nickName, fontsize=8, horizontalalignment='center', verticalalignment='center', color='deepskyblue')

    def set_tag(self, x, y, tagName):
        self.ax.scatter(x, y, marker='o', color='red', s=75)
        self.ax.text( x, y+0.5, tagName, fontsize=8, horizontalalignment='center', verticalalignment='center', color='red')
    
    def set_result_point(self, xy_list:list):
        for point_x, point_y in xy_list:
            self.ax.scatter(point_x, point_y, marker='.', color='blue', s=10)
    
    def show(self):
        plt.show()



anchor_list = [('anchor-a', 'ch37'), ('anchor-a', 'ch38'), ('anchor-a', 'ch39'),\
               ('anchor-b', 'ch37'), ('anchor-b', 'ch38'), ('anchor-b', 'ch39')]

if __name__ == '__main__':
    move_avg_count = 20
    A = position()
    A.set_system_config('system.ini')
    #print(A.config)
    A.get_measurement_data(1668673579000, 60000)
    A.set_anchor(anchor_list)
    A.set_tag('tag-a')
    print('-' * 25)
    print(A.raw_data)
    print('-' * 25)
    A.pltmap.show()
    plt.scatter(6.25, 6.25, marker='x', color='yellow', s=75) #tag r
    plt.title("T5 mov_avg="+ str(move_avg_count))
    os.system('PAUSE')
    

#========================================================================



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
        xy_list.append((x, y))
    except:
        print('', end='')
xy_df = pd.DataFrame(xy_list)
print(xy_df)
# xy_df.to_csv('T1.csv')



for point_x, point_y in xy_list:
    plt.scatter(point_x, point_y, marker='.', color='blue', s=10)

