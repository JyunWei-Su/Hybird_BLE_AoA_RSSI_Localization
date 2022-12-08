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
            df = pd.read_sql_query(f"SELECT unix_time, anchor_id, instance_id, rssi, azimuth, elevation, channel \
                    FROM measurement WHERE unix_time BETWEEN {start_time_ms} AND {start_time_ms+duration_ms}",con = conn)
            cur.close()
            if conn is not None:
                conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return df

#========================================================================
start_time = 1663479932000
#start_time = 1663480070000
#start_time = 1663480224000
#start_time = 1663480332000
#start_time = 1663480463000
#start_time = 1663480555000
anchor_list = ['anchor-a', 'anchor-b', 'anchor-c', 'anchor-d']
tag_list = ['tag-a']


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
        for channel in [37, 38, 39]:
            for tag in tag_list:
                mask_anchor = (df['anchor_id'] == anchor_id)
                mask_channel = (df['channel'] == channel)
                mask_tag = (df['instance_id'] == system_config[tag]['id'])
                temp = df[(mask_anchor & mask_channel & mask_tag)]
                temp = temp.resample('0.5S', on='time').mean() ##dddd
                temp = temp.drop(columns=['channel', 'unix_time'])
                temp['anchor'] = [anchor + '@ch' + str(channel)] * len(temp)
                temp['tag'] = [tag + '@' + str(system_config[tag]['tx_power'])] * len(temp)
                #print(temp)
                dfs.append(temp)
    elif anchor_type == 'rssi:esp32':
        for tag in tag_list:
            mask_anchor = (df['anchor_id'] == anchor_id)
            mask_tag = (df['instance_id'] == system_config[tag]['id'])
            temp = df[(mask_anchor & mask_tag)]
            temp = temp.resample('0.5S', on='time').mean()
            temp = temp.drop(columns=['channel', 'unix_time'])
            temp['anchor'] = [anchor + '@mix'] * len(temp)
            temp['tag'] = [tag + '@' + str(system_config[tag]['tx_power'])] * len(temp)
            #print(temp)
            dfs.append(temp)

measurement_data = pd.concat(dfs)
measurement_data = measurement_data.reset_index()
#print(measurement_data)
times = measurement_data['time']
times = times.drop_duplicates()
times = times.sort_values()
#print(times)
#print(measurement_data)
print('data_get')

def cal_loc(system_config:dict, df:pd.DataFrame):
    rssi_anchor_list = []
    for index in df.index: #   time    rssi  azimuth  elevation  anchor  tag
        anchor = df['anchor'][index]
        channel = anchor.split('@')[1]
        anchor_name = anchor.split('@')[0]
        anchor_type = system_config[anchor_name]['type']
        tag_tx = df['tag'][index].split('@')[1]
        if anchor_type == 'rssi+aoa:xplr-aoa':
            rssi = df['rssi'][index]
            azimuth = df['azimuth'][index]
            anchor_coordinate = np.asarray(system_config[anchor_name]['coordinate'])
            # print(anchor_coordinate)
            transform_matrix = np.asarray((system_config[anchor_name]['norm_vector'], system_config[anchor_name]['anim_vector']))
            # 算 R
            p0 = system_config[anchor_name]['p0'][channel] + float(tag_tx)
            gamma = system_config[anchor_name]['gamma'][channel]
            R = np.power(10, ((p0 - rssi) / gamma))
            # print('cal_R:', p0, rssi, gamma, R)
            # R = 10 ^ ((p0 - rssi) / gamma)
            cos_phi = np.cos(np.deg2rad(azimuth))
            sin_phi = np.sin(np.deg2rad(azimuth))
            # the following coordinate are stored in np.array type
            # x
            coordinate = np.asarray((R * cos_phi, 0))
            virtual_r = abs(R * sin_phi) ## abs???
            transformed_coord= transform_matrix @ coordinate + anchor_coordinate
            temp = pd.DataFrame([[transformed_coord[0], transformed_coord[1], virtual_r, anchor + 'x']], columns=['x', 'y', 'r', 'a'])
            rssi_anchor_list.append(temp) 
            # y
            coordinate = np.asarray((0, R * sin_phi))
            virtual_r = abs(R * cos_phi)
            transformed_coord= transform_matrix @ coordinate + anchor_coordinate
            temp = pd.DataFrame([[transformed_coord[0], transformed_coord[1], virtual_r, anchor + 'y']], columns=['x', 'y', 'r', 'a'])
            rssi_anchor_list.append(temp)
        elif anchor_type == 'rssi:esp32':
            rssi = df['rssi'][index]
            anchor_coordinate = np.asarray(system_config[anchor_name]['coordinate'])
            # 算 R
            p0 = system_config[anchor_name]['p0'][channel] + float(tag_tx)
            gamma = system_config[anchor_name]['gamma'][channel]
            R = np.power(10, ((p0 - rssi) / gamma))
            temp = pd.DataFrame([[anchor_coordinate[0], anchor_coordinate[1], R, anchor + 'r']], columns=['x', 'y', 'r', 'a'])
            rssi_anchor_list.append(temp) 

    rssi_anchor_df = pd.concat(rssi_anchor_list)
    #print(rssi_anchor_df)
    rssi_anchor_df = rssi_anchor_df[['r', 'x', 'y']]
    cal_list = rssi_anchor_df.values.tolist()
    #pp.pprint(cal_list)
    cal_list.sort(key=lambda x: x[0])
    #pp.pprint(cal_list)

    H = []
    b = []
    for index in range(1, len(cal_list)): ## r, x, y
        rrs = cal_list[0][0]**2
        arx = cal_list[0][1]
        ary = cal_list[0][2]
        rns = cal_list[index][0]**2
        anx = cal_list[index][1]
        any = cal_list[index][2]
        krs = arx**2 + ary**2
        kns = anx**2 + any**2
        H.append([anx-arx, any-ary])
        b.append([0.5 * (kns-krs-rns-rrs)])
    H = np.asarray(H)
    b = np.asarray(b)
    HT = H.T
    HTH_inv = la.inv(HT @ H)
    x_hat = HTH_inv @ HT @ b
    #print(H)
    #print(HT)
    #print(b)
    return x_hat

xy_list = []
for time_index in times.index:
    time = times[time_index]
    #print(time)
    data_on_time = measurement_data[measurement_data['time'] == time]
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
xy_df.to_csv('T1.csv')



#-------------------------

fig, ax = plt.subplots()
ax.set_ylim(-1, 13.5)
ax.set_xlim(-1, 19.5)
# Change major ticks to show every 20.
ax.xaxis.set_major_locator(MultipleLocator(6))
ax.yaxis.set_major_locator(MultipleLocator(6)) # 主要格線距離

# Change minor ticks to show every 5. (20/4 = 5)
ax.xaxis.set_minor_locator(AutoMinorLocator(12))
ax.yaxis.set_minor_locator(AutoMinorLocator(12)) # 切n段

# Turn grid on for both major and minor ticks and style minor slightly
# differently.
ax.grid(which='major', color='#CCCCCC', linestyle='--')
ax.grid(which='minor', color='#CCCCCC', linestyle=':')

tiles = []
for x in range(0, 37):
    for y in range(0, 25):
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

plot_anchor(   0,    0, 'Anchor B', 'xplr-aoa')
plot_anchor(18.5, 12.5, 'Anchor A', 'xplr-aoa')
plot_anchor(18.5,    0, 'Anchor C', 'esp32')
plot_anchor(   0, 12.5, 'Anchor D', 'esp32')

plt.scatter( 4.75, 7.75, marker='o', color='red', s=75) #tag p
plt.scatter(10.75, 7.75, marker='o', color='red', s=75) #tag q
plt.scatter(16.75, 7.75, marker='o', color='red', s=75) #tag r
plt.scatter( 1.75, 4.75, marker='o', color='red', s=75) #tag p
plt.scatter( 7.75, 4.75, marker='o', color='red', s=75) #tag q
plt.scatter(13.75, 4.75, marker='o', color='red', s=75) #tag r
ax.text(16.75, 7.75+0.5, 'T1', fontsize=8, horizontalalignment='center', verticalalignment='center', color='red')
ax.text(10.75, 7.75+0.5, 'T2', fontsize=8, horizontalalignment='center', verticalalignment='center', color='red')
ax.text( 4.75, 7.75+0.5, 'T3', fontsize=8, horizontalalignment='center', verticalalignment='center', color='red')
ax.text( 1.75, 4.75+0.5, 'T4', fontsize=8, horizontalalignment='center', verticalalignment='center', color='red')
ax.text( 7.75, 4.75+0.5, 'T5', fontsize=8, horizontalalignment='center', verticalalignment='center', color='red')
ax.text(13.75, 4.75+0.5, 'T6', fontsize=8, horizontalalignment='center', verticalalignment='center', color='red')

for point_x, point_y in xy_list:
    plt.scatter(point_x, point_y, marker='.', color='blue', s=10)


plt.scatter(16.75, 7.75, marker='x', color='yellow', s=75) #tag r


plt.show()

