from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from asyncio.windows_events import NULL
from email.headerregistry import ContentTransferEncodingHeader
from re import T
import secrets
from shutil import move
import sys
from tokenize import group
from django import conf
import psycopg2
import warnings ## bypass psycopg2 connection warning
from config import config
import pandas as pd
import numpy as np
from numpy.random import randn, random, uniform, multivariate_normal, seed
from numpy import linalg as la
import scipy.stats
import pprint as pp
import socket
import json
import os

# pf ex: https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python/blob/master/12-Particle-Filters.ipynb
from filterpy.monte_carlo import stratified_resample, residual_resample
import matplotlib as mpl
import matplotlib.pyplot as plt
    
import configparser
from datetime import datetime
# @see usage: https://www.delftstack.com/zh-tw/howto/python/python-ini-file/

#filename = "anchor.ini"


class ParticleFilter(object):

    def __init__(self, N, x_dim, y_dim):
        self.particles = np.empty((N, 3))  # x, y, heading
        self.N = N
        self.x_dim = x_dim
        self.y_dim = y_dim

        # distribute particles randomly with uniform weight
        self.weights = np.empty(N)
        self.weights.fill(1./N)
        self.particles[:, 0] = uniform(0, x_dim, size=N)   # x
        self.particles[:, 1] = uniform(0, y_dim, size=N)   # y
        self.particles[:, 2] = uniform(0, 2*np.pi, size=N) # w


    def predict(self, u, std):
        """ move according to control input u with noise std"""

        self.particles[:, 2] += u[0]
        self.particles[:, 2] %= 2 * np.pi

        d = u[1] + randn(self.N)
        self.particles[:, 0] += np.cos(self.particles[:, 2]) * d
        self.particles[:, 1] += np.sin(self.particles[:, 2]) * d

        self.particles[:, 0:2] += u + randn(self.N, 2) * std


    def weight(self, z, var):
        dist = np.sqrt((self.particles[:, 0] - z[0])**2 +
                       (self.particles[:, 1] - z[1])**2)

        # simplification assumes variance is invariant to world projection
        n = scipy.stats.norm(0, np.sqrt(var))
        prob = n.pdf(dist)

        # particles far from a measurement will give us 0.0 for a probability
        # due to floating point limits. Once we hit zero we can never recover,
        # so add some small nonzero value to all points.
        prob += 1.e-12
        self.weights += prob
        self.weights /= sum(self.weights) # normalize


    def neff(self):
        return 1. / np.sum(np.square(self.weights))


    def resample(self):
        p = np.zeros((self.N, 3))
        w = np.zeros(self.N)

        cumsum = np.cumsum(self.weights)
        for i in range(self.N):
            index = np.searchsorted(cumsum, random())
            p[i] = self.particles[index]
            w[i] = self.weights[index]

        self.particles = p
        self.weights.fill(1.0 / self.N)


    def estimate(self):
        """ returns mean and variance """
        pos = self.particles[:, 0:2]
        mu = np.average(pos, weights=self.weights, axis=0)
        var = np.average((pos - mu)**2, weights=self.weights, axis=0)

        return mu, var

def plot_pf(pf, xlim=100, ylim=100, weights=True):

    if weights:
        a = plt.subplot(221)
        a.cla()

        plt.xlim(0, ylim)
        #plt.ylim(0, 1)
        a.set_yticklabels('')
        plt.scatter(pf.particles[:, 0], pf.weights, marker='.', s=1, color='k')
        a.set_ylim(bottom=0)

        a = plt.subplot(224)
        a.cla()
        a.set_xticklabels('')
        plt.scatter(pf.weights, pf.particles[:, 1], marker='.', s=1, color='k')
        plt.ylim(0, xlim)
        a.set_xlim(left=0)
        #plt.xlim(0, 1)

        a = plt.subplot(223)
        a.cla()
    else:
        plt.cla()
    plt.scatter(pf.particles[:, 0], pf.particles[:, 1], marker='.', s=1, color='k')
    plt.xlim(0, xlim)
    plt.ylim(0, ylim)

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
    #pp.pprint(measurement_data)
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

def cal_location_once(anchors:list, tag:str, start_time_ms:int, end_time_ms:int):
    for anchor in ['anchor-a', 'anchor-b', 'anchor-c', 'anchor-d']: #'anchor-a', 'anchor-b', 'anchor-c', 'anchor-d'
        #print(f'====={anchor}=====')
        try:
            measurement_data[anchor] = get_measurement_data(system_config, anchor, tag, start_time_ms, end_time_ms)
        except ValueError as ex:
            print(f"{ex}")
        # basic R
        measurement_data[anchor]['basic']['R'] = cal_basic_R(system_config, anchor, measurement_data[anchor]['basic']['rssi'])
        
        if measurement_data[anchor]['isAoA']: #xplr-aoa
            measurement_data[anchor]['anchor'] = generate_virtual_anchor(measurement_data[anchor]['basic'])
            #print('Shape check:', np.shape(measurement_data[anchor]['anchor'][0]['coordinate']))
            measurement_data[anchor]['anchor'] = virtual_anchor_coordinate_transform(system_config, anchor, measurement_data[anchor]['anchor'])
            #print('Shape check:', np.shape(measurement_data[anchor]['anchor'][0]['coordinate']))
        else: #esp32
            measurement_data[anchor]['anchor'] = generate_anchor(system_config, anchor, measurement_data[anchor]['basic'])
        #pp.pprint(measurement_data)
    #pp.pprint(measurement_data)

    cal_anchor_list = extract_cal_anchor_list(measurement_data)

    #pp.pprint(cal_anchor_list)
    cal_anchor_list = sorted(cal_anchor_list, key=lambda x: x['R']) # sort using R https://note.nkmk.me/en/python-dict-list-sort/

    #pp.pprint(cal_anchor_list)

    H = generate_H(cal_anchor_list)
    b = generate_b(cal_anchor_list)
    #print(H)
    #print(b)
    HT = H.T
    #print('+' * 50)
    #print(H)
    #print('+' * 50)
    #print(HT)

    HTH_inv = la.inv(H.T @ H)
    #print('+' * 50)
    #print(HTH_inv)

    #x_hat = HTH_inv @ H.T @ b
    x_hat = HTH_inv @ H.T @ b
    #print('+' * 50)
    print(x_hat)
    return x_hat

# =====================SYSTEM MAIN========================

# 讀取系統配置
system_config = get_system_config("system.ini")
measurement_data = {}

# test
x_cal_pre = None
x_cal_now = None


N = 3000
pf = ParticleFilter(N, 18.5, 12.5)

z = np.array([4.75, 7.75]) 
z = cal_location_once(['anchor-a', 'anchor-b', 'anchor-c', 'anchor-d'], 'tag-b', 1658824770000 - 1000, 1658824770000)
z = z[0:2].T
z = z[0]
print(z)
#os.system('pause')
#plot(pf, weights=False)

time_step = 1000

for time in range(1658824770000, 1658824790000, time_step):
    x_cal_pre = cal_location_once(['anchor-a', 'anchor-b', 'anchor-c', 'anchor-d'], 'tag-b', time - time_step, time)
    x_cal_now = cal_location_once(['anchor-a', 'anchor-b', 'anchor-c', 'anchor-d'], 'tag-b', time, time + time_step)
    
    #z[0] = x_cal_pre[0]
    #z[1] = x_cal_pre[1]

    move_vector = x_cal_now - x_cal_pre
    move_vector = move_vector.T
    move_vector = (move_vector[0][0], move_vector[0][1])
    print(move_vector)

    pf.predict(move_vector, (0.2, 0.2)) # control input u (移動)
    pf.weight(z=z, var=.8) #計算權重
    pf.resample() #
    mu, var = pf.estimate()

    plot_pf(pf, 18.5, 12.5, weights=False)
    plt.scatter(mu[0], mu[1], color='g', s=100, label="PF")
    #理論值  4.75 7.75 1
    plt.scatter(4.75, 7.75, marker='x', color='r', s=180, label="True", lw=3)
    plt.legend(scatterpoints=1)
    plt.tight_layout()
    plt.pause(1)