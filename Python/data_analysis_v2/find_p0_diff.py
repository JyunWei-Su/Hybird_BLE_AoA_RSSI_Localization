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
import statistics

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

def list_avg(list_input):
    #print(list_input, len(list_input))
    if len(list_input) == 0:
        return 99999
    return sum(list_input)/len(list_input)

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
                df37 = pd.read_sql_query(f"SELECT stddev(rssi) as std, avg(rssi) as avg \
                        FROM measurement WHERE anchor_id='{anchor_id}' AND instance_id='{tag_id}' AND channel=37\
                            AND unix_time BETWEEN {start_time_ms} AND {start_time_ms+duration_ms}",con = conn)
                df38 = pd.read_sql_query(f"SELECT stddev(rssi) as std, avg(rssi) as avg \
                        FROM measurement WHERE anchor_id='{anchor_id}' AND instance_id='{tag_id}' AND channel=38\
                            AND unix_time BETWEEN {start_time_ms} AND {start_time_ms+duration_ms}",con = conn)
                df39 = pd.read_sql_query(f"SELECT stddev(rssi) as std, avg(rssi) as avg \
                        FROM measurement WHERE anchor_id='{anchor_id}' AND instance_id='{tag_id}' AND channel=39\
                            AND unix_time BETWEEN {start_time_ms} AND {start_time_ms+duration_ms}",con = conn)
            '''
            try:
                df37 = df37['rssi'].values.tolist()
                df37 = statistics.mode(df37)
            except:
                df_37 = 99999
            #df37.sort()
            #df37 = df37[int(len(df37)*0.1) : int(len(df37)*0.9)]
            try:
                df38 = df38['rssi'].values.tolist()
                df38 = statistics.mode(df38)
            except:
                df38 = 99999
            #df38.sort()
            #df38 = df38[int(len(df38)*0.1) : int(len(df38)*0.9)]
            try:
                df39 = df39['rssi'].values.tolist()
                df39 = statistics.mode(df39)
            except:
                df39 = 99999
            #df39.sort()
            #df39 = df39[int(len(df39)*0.1) : int(len(df39)*0.9)]
            '''

            #os.system('pause')
            cur.close()
            if conn is not None:
                conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return df37['std'][0], df37['avg'][0], df38['std'][0], df38['avg'][0], df39['std'][0], df39['avg'][0]
    # return list_avg(df37), list_avg(df38), list_avg(df39)

    # return df37, df38 ,df39

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
            df = pd.read_sql_query(f"SELECT stddev(rssi) as std, avg(rssi) as avg \
                    FROM measurement WHERE anchor_id='{anchor_id}' AND instance_id='{tag_id}' \
                        AND unix_time BETWEEN {start_time_ms} AND {start_time_ms+duration_ms}",con = conn)
            cur.close()
            if conn is not None:
                conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return df['std'][0], df['avg'][0]



#========================================================================

time_list = [1671434829046, 1671434933122, 1671435034437, \
    1671435198902, 1671435320219, 1671435425196, 1671435560253, \
        1671435892648, 1671435986849, 1671436069583, \
    1671436163954, 1671436261975, 1671436426924, 1671436534890]

tag_id = '6C1DEBA41680'
for time in time_list:
    a_37_std, a_37_avg, a_38_std, a_38_avg, a_39_std, a_39_avg = get_measurement_data_anchor_channel(time, 60000, '6C1DEBA097F3', tag_id, 'all')
    b_37_std, b_37_avg, b_38_std, b_38_avg, b_39_std, b_39_avg = get_measurement_data_anchor_channel(time, 60000, '6C1DEBA097FA', tag_id, 'all')
    c_std, c_avg = get_measurement_data_rssi_esp32(time, 60000, 'B8D61A822CAC', tag_id)
    d_std, d_avg = get_measurement_data_rssi_esp32(time, 60000, '24D7EB0B2004', tag_id)
    #print(time, a_37, a_38, a_39, b_37, b_38, b_39)

    '''
    diff_37, diff_38, diff_39, diff_cd = 0, 0, 0, 0
    try:
        diff_37 = a_37 - b_37
    except:
        diff_37 = 'error'
    try:
        diff_38 = a_38 - b_38
    except:
        diff_38 = 'error'
    try:
        diff_39 = a_39 - b_39
    except:
        diff_39 = 'error'
    try:
        diff_cd = c - d
    except:
        diff_cd = 'error'
    '''
    def myround(data):
        if data != None:
            return round(data, 1)
        else:
            return '-'
    print(time, myround(a_37_std), myround(a_37_avg), myround(a_38_std), myround(a_38_avg), myround(a_39_std), myround(a_39_avg), \
        myround(b_37_std), myround(b_37_avg), myround(b_38_std), myround(b_38_avg), myround(b_39_std), myround(b_39_avg), \
        myround(c_std), myround(c_avg), myround(d_std), myround(d_avg), sep='\t')