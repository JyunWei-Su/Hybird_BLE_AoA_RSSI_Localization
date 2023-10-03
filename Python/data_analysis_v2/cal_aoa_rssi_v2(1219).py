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

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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

def find_regression_line(coordinate:list):
    x = []
    y = []
    for coo in coordinate:
        x.append(coo[0])
        y.append(coo[1])
    line = np.polyfit(x, y, 1)     #https://numpy.org/doc/stable/reference/generated/numpy.polyfit.html
    return line                    #let line = ax+b ,a = line[0], b = line[1] 

def euclidean_distance(points:list, line:list):
    k = line[0]
    h = line[1]
    Distance = []
    for (x, y) in points:
        Distance.append(math.fabs(h+k*x-y)/(math.sqrt(k*k+1)))  #https://zhuanlan.zhihu.com/p/344482100
    return Distance

def objection(points:list, line:list):
    k = line[0]
    h = line[1]
    obj = []
    for (x, y) in points:
        obj.append(((k*(y-h)+x)/(k*k+1) , k*(k*(y-h)+x)/(k*k+1)+h))
    return obj

def p2p(point_a, point_b):
    diff_x = point_a[0] - point_b[0]
    diff_y = point_a[1] - point_b[1]
    return math.sqrt(diff_x * diff_x + diff_y * diff_y)


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

def get_measurement_data_anchor_channel(start_time_ms:int, duration_ms:int, anchor_id, tag_id, channel): # time format in ms
    conn = None
    cur = None
    df37, df38, df39 = None, None, None
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
            if channel != None:
                df37 = pd.read_sql_query(f"SELECT avg(rssi) \
                        FROM measurement WHERE anchor_id='{anchor_id}' AND instance_id='{tag_id}' AND channel=37\
                            AND unix_time BETWEEN {start_time_ms} AND {start_time_ms+duration_ms}",con = conn)
                df38 = pd.read_sql_query(f"SELECT avg(rssi) \
                        FROM measurement WHERE anchor_id='{anchor_id}' AND instance_id='{tag_id}' AND channel=38\
                            AND unix_time BETWEEN {start_time_ms} AND {start_time_ms+duration_ms}",con = conn)
                df39 = pd.read_sql_query(f"SELECT avg(rssi) \
                        FROM measurement WHERE anchor_id='{anchor_id}' AND instance_id='{tag_id}' AND channel=39\
                            AND unix_time BETWEEN {start_time_ms} AND {start_time_ms+duration_ms}",con = conn)
            cur.close()
            if conn is not None:
                conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return df37['avg'][0], df38['avg'][0], df39['avg'][0]

def get_measurement_data_rssi_esp32(start_time_ms:int, duration_ms:int, anchor_id, tag_id): # time format in ms
    conn = None
    cur = None
    df= None
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
            df = pd.read_sql_query(f"SELECT avg(rssi) \
                    FROM measurement WHERE anchor_id='{anchor_id}' AND instance_id='{tag_id}' \
                        AND unix_time BETWEEN {start_time_ms} AND {start_time_ms+duration_ms}",con = conn)
            cur.close()
            if conn is not None:
                conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return df['avg'][0]

#========================================================================
# point   start_time     tag     answer
# T1      1668672951000  tag-b   9.25, 3.25
# T2      1668673044000  tag-b   3.25, 3.25
# T3      1668673215000  tag-a   3.25, 9.25
# T4      1668673417000  tag-b   9.25, 9.25
# T5      1668673579000  tag-a   6.25, 6.25
test_point = {
'T1': {'start_time': 1671437768128, 'tag': 'tag-a', 'answer':(9.25, 3.25)},
'T2': {'start_time': 1671438033459, 'tag': 'tag-a', 'answer':(3.25, 3.25)},
'T3': {'start_time': 1671438177516, 'tag': 'tag-a', 'answer':(3.25, 9.25)},
'T4': {'start_time': 1671438274390, 'tag': 'tag-a', 'answer':(9.25, 9.25)},
'T5': {'start_time': 1671438382390, 'tag': 'tag-a', 'answer':(6.25, 6.25)}
}
# T1 
# T2 
# T3 
# T4 
# T5 

CAL_POINT = 'T4' 
anchor_list = ['anchor-a', 'anchor-b']
tag_list = [test_point[CAL_POINT]['tag']]
start_time = test_point[CAL_POINT]['start_time']
move_avg_count = 5
answer = test_point[CAL_POINT]['answer']
POINT = CAL_POINT


system_config = get_system_config("system.ini")
print('config get')
df = get_measurement_data(start_time, 60000)
a_37_rssi, a_38_rssi, a_39_rssi = get_measurement_data_anchor_channel(start_time, 60000, system_config['anchor-a']['id'], system_config[tag_list[0]]['id'], 'all')
b_37_rssi, b_38_rssi, b_39_rssi = get_measurement_data_anchor_channel(start_time, 60000, system_config['anchor-b']['id'], system_config[tag_list[0]]['id'], 'all')
a_37_p0 = system_config['anchor-a']['p0']['ch37'] + system_config[tag_list[0]]['tx_power']
a_38_p0 = system_config['anchor-a']['p0']['ch38'] + system_config[tag_list[0]]['tx_power']
a_39_p0 = system_config['anchor-a']['p0']['ch39'] + system_config[tag_list[0]]['tx_power']
b_37_p0 = system_config['anchor-b']['p0']['ch37'] + system_config[tag_list[0]]['tx_power']
b_38_p0 = system_config['anchor-b']['p0']['ch38'] + system_config[tag_list[0]]['tx_power']
b_39_p0 = system_config['anchor-b']['p0']['ch39'] + system_config[tag_list[0]]['tx_power']
a_37_gamma = system_config['anchor-a']['gamma']['ch37']
a_38_gamma = system_config['anchor-a']['gamma']['ch38']
a_39_gamma = system_config['anchor-a']['gamma']['ch39']
b_37_gamma = system_config['anchor-b']['gamma']['ch37']
b_38_gamma = system_config['anchor-b']['gamma']['ch38']
b_39_gamma = system_config['anchor-b']['gamma']['ch39']
a_pos = (12.5, 0)
b_pos = (0, 0)
c_rssi = get_measurement_data_rssi_esp32(start_time, 60000, system_config['anchor-c']['id'], system_config[tag_list[0]]['id'])
d_rssi = get_measurement_data_rssi_esp32(start_time, 60000, system_config['anchor-d']['id'], system_config[tag_list[0]]['id'])
c_p0 = system_config['anchor-c']['p0']['mix'] + system_config[tag_list[0]]['tx_power']
d_p0 = system_config['anchor-d']['p0']['mix'] + system_config[tag_list[0]]['tx_power']
c_gamma = system_config['anchor-c']['gamma']['mix']
d_gamma = system_config['anchor-d']['gamma']['mix']
d_pos = (0, 12.5)
c_pos = (12.5, 12.5)

print(a_37_rssi, a_38_rssi, a_39_rssi)
print(b_37_rssi, b_38_rssi, b_39_rssi)

df['time'] = pd.to_datetime(df['unix_time'], unit='ms', utc=True).dt.strftime('%Y-%m-%d %H:%M:%S.%f')
df['time'] = df['time'].apply(pd.Timestamp)
print(df)

dfs = []

for anchor in anchor_list:
    anchor_type = system_config[anchor]['type']
    anchor_id = system_config[anchor]['id']
    if anchor_type == 'rssi+aoa:xplr-aoa':
        for tag in tag_list:
            try:
                mask_anchor = (df['anchor_id'] == anchor_id)
                mask_tag = (df['instance_id'] == system_config[tag]['id'])
                temp = df[(mask_anchor & mask_tag)]
                temp = temp.resample('0.5S', on='time').mean() ##dddd
                temp = temp.drop(columns=[ 'unix_time'])
                temp['anchor'] = [anchor + '@chmix'] * len(temp)
                if(anchor == 'anchor-a'):
                    temp['azimuth'] = temp['azimuth'] - 45
                elif(anchor == 'anchor-b'):
                    temp['azimuth'] = temp['azimuth'] + 45
                #temp['tag'] = [tag + '@' + str(system_config[tag]['tx_power'])] * len(temp)
                #print(temp)
                dfs.append(temp)
            except:
                print(anchor, 'error')

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

def tuple_avg(lst):
    x = []
    y = []
    for coo in lst:
        x.append(coo[0])
        y.append(coo[1])
    return (avg(x), avg(y))

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


#print(times.index)
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
    #print(time)
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
#print(xy_list)
xy_df = pd.DataFrame(xy_list)
result_aoa = tuple_avg(xy_list)
error_aoa_x = answer[0] - result_aoa[0]
error_aoa_y = answer[1] - result_aoa[1]
error_aoa = math.sqrt(error_aoa_x * error_aoa_x + error_aoa_y * error_aoa_y)
#print(xy_df)
std_x = xy_df[0].std()
std_y = xy_df[1].std()
diverge_range = math.sqrt(std_x * std_x + std_y * std_y)
print('std_x:', std_x)
print('std_y:', std_y)
# xy_df.to_csv('T1.csv')
r, p = stats.pearsonr(xy_df[0], xy_df[1])  # 相關係數r和p值
print('相關係數r^2 = %6.3f, p = %6.3f' % (r * r, p))

print('=====單純使用AoA=====')
print(round(result_aoa[0], 2), round(result_aoa[1], 2))
print('誤差:', round(error_aoa, 2), 'm')

print('=====使用RSSI輔助=====')
#let line = ax+b ,a = line[0], b = line[1] 
line = find_regression_line(xy_list)
#print('回歸線: y=', round(line[0], 2), 'x +', round(line[1], 2))
objection_point = objection([result_aoa], line)
objection_point = objection_point[0]
# 發散n個點 每0.1斜率
diverge_points = [objection_point]
diverge_count = 1
while(True):
    point_p = (objection_point[0] + 0.1 * diverge_count, objection_point[1] + 0.1 * diverge_count * line[0])
    point_m = (objection_point[0] - 0.1 * diverge_count, objection_point[1] - 0.1 * diverge_count * line[0])
    if(p2p(point_p, objection_point) <= 10 * diverge_range):
        diverge_points.append(point_p)
        diverge_points.append(point_m)
        diverge_count += 1
    else:
        break
diverge_points_error = [0] * len(diverge_points)
for index, point in enumerate(diverge_points):
    # print(index, point)
    temp_error = 0
    # a 37
    RSSI_A37 = a_37_p0 - a_37_gamma * np.log10(p2p(point, a_pos))
    # a 38
    RSSI_A38 = a_38_p0 - a_38_gamma * np.log10(p2p(point, a_pos))
    # a 39
    RSSI_A39 = a_39_p0 - a_39_gamma * np.log10(p2p(point, a_pos))
    # b 37
    RSSI_B37 = b_37_p0 - b_37_gamma * np.log10(p2p(point, b_pos))
    # b 38
    RSSI_B38 = b_38_p0 - b_38_gamma * np.log10(p2p(point, b_pos))
    # b 39
    RSSI_B39 = b_39_p0 - b_39_gamma * np.log10(p2p(point, b_pos))
    # c
    RSSI_C = c_p0 - c_gamma * np.log10(p2p(point, c_pos))
    # d
    RSSI_D = d_p0 - d_gamma * np.log10(p2p(point, d_pos))
    # debug print
    # print(p2p(point, a_pos), RSSI_A37, RSSI_B37, RSSI_C, RSSI_D)

    DIFF_37 = (RSSI_A37 - RSSI_B37) - (a_37_rssi - b_37_rssi) +8
    DIFF_38 = (RSSI_A38 - RSSI_B38) - (a_38_rssi - b_38_rssi) +12
    DIFF_39 = (RSSI_A39 - RSSI_B39) - (a_39_rssi - b_39_rssi)
    # DIFF_CD = (RSSI_C - RSSI_D) - (c_rssi - d_rssi) 
    DIFF_37 = abs(DIFF_37)
    DIFF_38 = abs(DIFF_38)
    DIFF_39 = abs(DIFF_39)
    #DIFF_CD = abs(DIFF_CD)
    DIFF_CD = 0
    print(point, DIFF_37, DIFF_38, DIFF_39, DIFF_CD, sep='\t')
    temp_error = abs(DIFF_37) + abs(DIFF_38) + abs(DIFF_39) + abs(DIFF_CD) - 0* max(DIFF_37, DIFF_38, DIFF_39, DIFF_CD)
    diverge_points_error[index] = temp_error

for index, point in enumerate(diverge_points):
    #print(index, round(diverge_points_error[index], 2), point, sep='\t')
    pass

#print(diverge_points)
result_aoa_rssi = diverge_points[diverge_points_error.index(min(diverge_points_error))]
#print(result_aoa_rssi)
error_aoa_rssi_x = answer[0] - result_aoa_rssi[0]
error_aoa_rssi_y = answer[1] - result_aoa_rssi[1]
error_aoa_rssi = math.sqrt(error_aoa_rssi_x * error_aoa_rssi_x + error_aoa_rssi_y * error_aoa_rssi_y)
print(round(result_aoa_rssi[0], 2), round(result_aoa_rssi[1], 2))
print('誤差:', round(error_aoa_rssi, 2), 'm')


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
    plt.scatter(point_x, point_y, marker='.', color='lightblue', s=10)

for point_x, point_y in diverge_points:
    plt.scatter(point_x, point_y, marker='.', color='violet', s=10)

# print(xy_list)


plt.scatter(result_aoa[0], result_aoa[1], marker='x', color='blue', s=75)
plt.scatter(result_aoa_rssi[0], result_aoa_rssi[1], marker='x', color='purple', s=75)
plt.scatter(answer[0], answer[1], marker='x', color='yellow', s=75)

plt.title(POINT + " mov_avg="+ str(move_avg_count) + '')

plt.show()
