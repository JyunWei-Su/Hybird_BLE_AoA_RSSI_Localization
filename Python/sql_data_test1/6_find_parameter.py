from asyncio.windows_events import NULL
from email.headerregistry import ContentTransferEncodingHeader
from msilib import AMD64
from re import T
import secrets
import sys
from tokenize import group
from django import conf
import psycopg2
import warnings ## bypass psycopg2 connection warning
from config import config
import pandas as pd
import cupy as cp
from cupy import linalg as la
cp.cuda.Device(0).use()
print('Using cupy')
import numpy as np
#from numpy import linalg as npla
print('Using numpy')
import pprint as pp
import socket
import json
import os 

# Listen for incoming datagrams
    
import configparser
from datetime import datetime
# @see usage: https://www.delftstack.com/zh-tw/howto/python/python-ini-file/

#filename = "anchor.ini"

# get the anchor config from config file
def get_system_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    config_dict = config._sections
    for instance in [section for section in config.sections() if 'anchor' in section or 'tag' in section]:
        if 'eval_keys' in config_dict[instance]:
            config_dict[instance]['eval_keys'] = eval(config_dict[instance]['eval_keys'])
            for key in config_dict[instance]['eval_keys']:
                config_dict[instance][key] = eval(config_dict[instance][key])
        else:
            print(f'Error with config file(section: {instance}).')
    return config_dict

def get_measurement_data(system_config:dict, anchor_name:str, tag_name:str, start_time_ms:int, end_time_ms:int): # time format in ms
    anchor_type = system_config[anchor_name]['type']
    anchor_id = system_config[anchor_name]['id']
    tag_id = system_config[tag_name]['id']

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
            isAoA = False
            if(anchor_type == 'rssi+aoa:xplr-aoa'):
                isAoA = True
                df = pd.read_sql_query(f"SELECT AVG(rssi) AS rssi_avg, AVG(azimuth) AS azimuth_avg, AVG(elevation) AS elevation_avg\
                                        FROM measurement WHERE anchor_id='{anchor_id}' AND instance_id='{tag_id}' \
                                        AND unix_time BETWEEN {start_time_ms} AND {end_time_ms}",con = conn)
            elif(anchor_type == 'rssi:esp32'):
                df = pd.read_sql_query(f"SELECT AVG(rssi) AS rssi_avg\
                                        FROM measurement WHERE anchor_id='{anchor_id}' AND instance_id='{tag_id}' \
                                        AND unix_time BETWEEN {start_time_ms} AND {end_time_ms}",con = conn)
            #print(df)
            #os.system('pause')
            cur.close()
            if conn is not None:
                conn.close()
            # execute the INSERT statement

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    # format to dictionary
    measurement_data = {}
    # attributes data
    measurement_data['isAoA'] = isAoA
    # basic measurement
    measurement_data['basic'] = {}
    measurement_data['basic']['rssi'] = df['rssi_avg'][0] # <class 'numpy.float64'>
    if isAoA:
        measurement_data['basic']['azimuth'] = df['azimuth_avg'][0] # <class 'numpy.float64'>
        measurement_data['basic']['elevation'] = df['elevation_avg'][0] # <class 'numpy.float64'>
    #pp.pprint(measurement_data)
    return measurement_data

def cal_basic_R_spec_parm(rssi, p0, gamma):
    #print(rssi, p0, gamma)
    R = np.power(10, ((p0 - rssi) / gamma))
    # print('cal_R:', p0, rssi, gamma, R)
    # R = 10 ^ ((p0 - rssi) / gamma)
    return R

def generate_anchor(system_config:dict, anchor_name:str, basic_measure_data:dict):
    coordinate = np.asarray(system_config[anchor_name]['coordinate']).T
    anchor = []
    anchor.append({'R': basic_measure_data['R'], \
                   'coordinate': coordinate, \
                   'K': la.norm(coordinate)})
    return anchor

def generate_virtual_anchor(basic_measure_data:dict):
    R = basic_measure_data['R']
    azimuth = basic_measure_data['azimuth']
    elevation = basic_measure_data['elevation']

    cos_theta = np.cos(np.deg2rad(elevation)) # need to transform deg to rad
    sin_theta = np.sin(np.deg2rad(elevation))
    cos_phi = np.cos(np.deg2rad(azimuth))
    sin_phi = np.sin(np.deg2rad(azimuth))
    virtual_anchor = []
    # the following coordinate are stored in np.array type
    # x
    coordinate = (R * cos_theta * cos_phi, 0, 0)
    virtual_r = R * np.sqrt(1 - np.power(cos_theta, 2) * np.power(cos_phi, 2))
    virtual_anchor.append({'coordinate': np.asarray(coordinate).T, 'R': virtual_r, 'transformed' : False})
    # y
    coordinate = (0, R * cos_theta * sin_phi, 0)
    virtual_r = R * np.sqrt(1 - np.power(cos_theta, 2) * np.power(sin_phi, 2))
    virtual_anchor.append({'coordinate': np.asarray(coordinate).T, 'R': virtual_r, 'transformed' : False})
    # z
    coordinate = (0, 0, R * sin_theta)
    virtual_r = R * cos_theta
    virtual_anchor.append({'coordinate': np.asarray(coordinate).T, 'R': virtual_r, 'transformed' : False})

    return virtual_anchor

def virtual_anchor_coordinate_transform(system_config:dict, anchor_name:str, virtual_anchor_list:list):
    # the following calculations' vetcor are in col vector form (.T)
    anchor_coordinate = np.asarray(system_config[anchor_name]['coordinate']).T
    transform_matrix = np.asarray((system_config[anchor_name]['norm_vector'],\
                                   system_config[anchor_name]['anim_vector'],\
                                   system_config[anchor_name]['elev_vector'])).T # row vector form
    #transform_matrix = np.transpose(transform_matrix) # transform to col vector form
    #print(anchor_coordinate)
    #print(transform_matrix)
    transformed = []
    for virtual_anchor in virtual_anchor_list:
        temp = {}
        temp['R'] = virtual_anchor['R']
        #print('virtual coord.:', virtual_anchor['coordinate'])
        temp['coordinate'] = transform_matrix @ virtual_anchor['coordinate'] + anchor_coordinate
        temp['transformed'] = True
        temp['K'] = la.norm(temp['coordinate'])
        transformed.append(temp)
    
    return transformed

def extract_cal_anchor_list(measurement_data:dict):
    cal_anchor_list = []
    for anchor in measurement_data.keys():
        for data in measurement_data[anchor]['anchor']:
            if 'transformed' in data.keys():
                del data['transformed']
            cal_anchor_list.append(data)
        # 移掉 'transformed' 屬性 https://stackoverflow.com/questions/5844672/delete-an-element-from-a-dictionary
        # cal_anchor_list += measurement_data[anchor]['anchor']
    return cal_anchor_list

def generate_H(cal_anchor_list_sorted:list):
    length =  len(cal_anchor_list_sorted)
    H = np.empty((length - 1, 3))
    
    for index in range(1, length):
        H[index - 1 : ] = cal_anchor_list_sorted[index]['coordinate'] - cal_anchor_list_sorted[0]['coordinate']
    return H

def generate_b(cal_anchor_list_sorted:list):
    length =  len(cal_anchor_list_sorted)
    b = np.zeros((length - 1, 1))
    kr = cal_anchor_list_sorted[0]['K']
    rr = cal_anchor_list_sorted[0]['R']
    for index in range(1, length):
        ki = cal_anchor_list_sorted[index]['K']
        ri = cal_anchor_list_sorted[index]['R']
        b[index - 1] =  0.5 * (ki ** 2 - kr ** 2 - ri ** 2 + rr ** 2)
    return b

enum_parm = []
for p0a in range(-40, -60, -1):
    for p0b in range(-40, -60, -1):
        for p0c in range(-40, -60, -1):
            for p0d in range(-40, -60, -1):
                for gamma in range(15,20, 1):
                    enum_parm.append({'anchor-a': p0a, 'anchor-b': p0b, 'anchor-c': p0c, 'anchor-d': p0d, 'gamma': gamma})
                    #print(count, ':', p0a, p0b, p0c, p0d, gamma)
        print('.', end='')
    print('.')

total = len(enum_parm)

system_config = get_system_config("system.ini")

start_time  = 1658824770000
end_time = 1658824790000
time_step = 100 # ms
x_bound = (0, 18.5)
y_bound = (0, 12.5)
z_bound = (0, 20)
cache = {}

count = 0
for parm in enum_parm:
    for time in range(start_time, end_time, time_step):
        measurement_data = {}

        for anchor in ['anchor-a', 'anchor-b', 'anchor-c', 'anchor-d']: #'anchor-a', 'anchor-b', 'anchor-c', 'anchor-d'
            #print(anchor, time)
            #print(f'====={anchor}=====')
            if (anchor + str(time)) not in cache.keys():
                try:
                    measurement_data[anchor] = get_measurement_data(system_config, anchor, 'tag-b', time, time + time_step)
                    cache[anchor + str(time)] = measurement_data[anchor]
                    print('.', end='')
                except ValueError as ex:
                    print(f"{ex}")
            else:
                measurement_data[anchor] = cache[anchor + str(time)]
            
            # basic R
            try:
                measurement_data[anchor]['basic']['R'] = cal_basic_R_spec_parm(measurement_data[anchor]['basic']['rssi'], parm[anchor] ,parm['gamma'])
            except:
                continue
            
            if measurement_data[anchor]['isAoA']: #xplr-aoa
                measurement_data[anchor]['anchor'] = generate_virtual_anchor(measurement_data[anchor]['basic'])
                #print('Shape check:', np.shape(measurement_data[anchor]['anchor'][0]['coordinate']))
                measurement_data[anchor]['anchor'] = virtual_anchor_coordinate_transform(system_config, anchor, measurement_data[anchor]['anchor'])
                #print('Shape check:', np.shape(measurement_data[anchor]['anchor'][0]['coordinate']))
            else: #xplr-aoa
                measurement_data[anchor]['anchor'] = generate_anchor(system_config, anchor, measurement_data[anchor]['basic'])
            #pp.pprint(measurement_data)

        #pp.pprint(measurement_data)
        try:
            cal_anchor_list = extract_cal_anchor_list(measurement_data)
        except:
            continue

        #pp.pprint(cal_anchor_list)
        cal_anchor_list = sorted(cal_anchor_list, key=lambda x: x['R']) # sort using R https://note.nkmk.me/en/python-dict-list-sort/

        #pp.pprint(cal_anchor_list)

        H = generate_H(cal_anchor_list)
        b = generate_b(cal_anchor_list)
        HT = H.T

        HTH_inv = la.inv(H.T @ H)

        x_hat = HTH_inv @ H.T @ b
        
        #print(x_hat)
        x = x_hat[0]
        y = x_hat[1]
        z = x_hat[2]
        if x_bound[0] <= x <= x_bound[1] and \
           y_bound[0] <= y <= y_bound[1] and \
           z_bound[0] <= z <= z_bound[1] :
            print('\n', '-'*10, parm, time)
            print(x, y, z)
        #os.system('pause')
        #else:
            #print('.', end='')
    count += 1
    if (count % 100) == 0:
        print(str(count) +'/' + str(total))
print('\n++++++++++++++++++++++ Done ++++++++++++++++++++++++++')
# calculate