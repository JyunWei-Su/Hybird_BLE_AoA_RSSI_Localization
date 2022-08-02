from asyncio.windows_events import NULL
from email.headerregistry import ContentTransferEncodingHeader
from re import T
import secrets
import sys
from tokenize import group
from django import conf
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

    p0 = system_config[anchor_name]['p0']
    gamma = system_config[anchor_name]['gamma']

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
    measurement_data['p0'] = p0
    measurement_data['gamma'] = gamma
    # basic measurement
    measurement_data['basic'] = {}
    measurement_data['basic']['rssi'] = df['rssi_avg'][0] # <class 'numpy.float64'>
    if isAoA:
        measurement_data['basic']['azimuth'] = df['azimuth_avg'][0] # <class 'numpy.float64'>
        measurement_data['basic']['elevation'] = df['elevation_avg'][0] # <class 'numpy.float64'>
    #print(measurement_data)
    return measurement_data

def cal_basic_R(system_config:dict, anchor_name:str, rssi):
    p0 = system_config[anchor_name]['p0']
    gamma = system_config[anchor_name]['gamma']
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


system_config = get_system_config("system.ini")
measurement_data = {}
# pp.pprint(system_config)
for anchor in ['anchor-b', 'anchor-c', 'anchor-d']: #'anchor-a', 'anchor-b', 'anchor-c', 'anchor-d'
    print(f'====={anchor}=====')
    try:
        measurement_data[anchor] = get_measurement_data(system_config, anchor, 'tag-b', 1658824700000, 1658824701000)
    except ValueError as ex:
        print(f"{ex}")
    # basic R
    measurement_data[anchor]['basic']['R'] = cal_basic_R(system_config, anchor, measurement_data[anchor]['basic']['rssi'])
    
    if measurement_data[anchor]['isAoA']: #xplr-aoa
        measurement_data[anchor]['anchor'] = generate_virtual_anchor(measurement_data[anchor]['basic'])
        #print('Shape check:', np.shape(measurement_data[anchor]['anchor'][0]['coordinate']))
        measurement_data[anchor]['anchor'] = virtual_anchor_coordinate_transform(system_config, anchor, measurement_data[anchor]['anchor'])
        #print('Shape check:', np.shape(measurement_data[anchor]['anchor'][0]['coordinate']))
    else: #xplr-aoa
        measurement_data[anchor]['anchor'] = generate_anchor(system_config, anchor, measurement_data[anchor]['basic'])
    #pp.pprint(measurement_data)

pp.pprint(measurement_data)

cal_anchor_list = extract_cal_anchor_list(measurement_data)

#pp.pprint(cal_anchor_list)
cal_anchor_list = sorted(cal_anchor_list, key=lambda x: x['R']) # sort using R https://note.nkmk.me/en/python-dict-list-sort/

pp.pprint(cal_anchor_list)

H = generate_H(cal_anchor_list)
b = generate_b(cal_anchor_list)
#print(H)
#print(b)
HT = H.T
print('+' * 50)
print(H)
print('+' * 50)
print(HT)

HTH_inv = la.inv(H.T @ H)
print('+' * 50)
print(HTH_inv)

#x_hat = HTH_inv @ H.T @ b
x_hat = HTH_inv @ H.T
print('+' * 50)
print(x_hat)

x_hat = x_hat @ b
print('+' * 50)
print(x_hat)




# calculate
