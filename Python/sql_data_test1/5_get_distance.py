from re import T
from sqlite3 import Timestamp
from tokenize import group
import psycopg2
from config import config
import pandas as pd
import numpy as np
import pprint as pp
import seaborn as sns
import matplotlib.pyplot as plt
import socket
import json
import os 
import csv

# Listen for incoming datagrams
    
import configparser
from datetime import datetime
# @see usage: https://www.delftstack.com/zh-tw/howto/python/python-ini-file/

#filename = "anchor.ini"


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

def get_measurement_data(anchor_config:dict, anchor_name:str, start_time:int, end_time:int): # time format in second
    try:
        start = datetime.fromtimestamp(start_time)
        end = datetime.fromtimestamp(end_time)
        delta = end - start
    except:
        raise ValueError('Time format error. ')
    
    start_time_ms = start_time * 1000
    end_time_ms = end_time * 1000
    id = anchor_config[anchor_name]['id']

    conn = None
    cur = None
    df = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        conn.autocommit = True
        # create a new cursor
        cur = conn.cursor()

        # https://stackoverflow.com/questions/27884268/return-pandas-dataframe-from-postgresql-query-with-sqlalchemy
        df = pd.read_sql_query(f"SELECT unix_time, rssi, azimuth, elevation \
                                 FROM measurement WHERE anchor_id='{id}' AND instance_id='6C1DEBA42193' \
                                 AND unix_time BETWEEN {start_time_ms} AND {end_time_ms} \
                                 ORDER BY unix_time asc",con = conn)
        # or SELECT * FROM measurement WHERE anchor_id='6C1DEBA097FA' AND to_timestamp(unix_time::double precision /1000) BETWEEN timestamp '2022-07-14 23:28:20.000' AND timestamp '2022-07-15 23:28:30.000';
        #print(df)
        #os.system('pause')
        cur.close()
        if conn is not None:
            conn.close()
        # execute the INSERT statement

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    return df


anchor_config = get_system_config("system.ini")
#pp.pprint(anchor_config)

time_list =  [1662972623,1662972688,1662972820,1662972889,1662972974,1629973045,
              1662973126,1662973193,1662973260,1662973351,1662973447,1662973529,
              1662973613,1662973722,1662973789,1662973898,1662974030,1662974144]

for timestamp in time_list:
    data_A = None
    data_B = None
    data_C = None
    data_D = None
    timestamp5 = timestamp+5
    timestamp25 = timestamp+25
    rssi = []

    try:
        data_A = get_measurement_data(anchor_config, 'anchor-a', timestamp5, timestamp25)
        data_B = get_measurement_data(anchor_config, 'anchor-b', timestamp5, timestamp25)
        data_C = get_measurement_data(anchor_config, 'anchor-c', timestamp5, timestamp25)
        data_D = get_measurement_data(anchor_config, 'anchor-d', timestamp5, timestamp25)
    except ValueError as ex:
        print(f"{ex}")

    for measurement_data in [data_A,data_B,data_C,data_D]:
        mean = measurement_data['rssi'].mean()
        rssi.append(mean)
    print(rssi)
    with open('result_0912_A.csv','a',newline = '\n') as f:
        writer = csv.writer(f)
        writer.writerow(rssi)


#print(measurement_data)
#measurement_data.to_csv('result_0908.csv', mode='a', index=True, header=True)
#cut_range = np.arange(1657845678000, 1657845878000, 1000)
#segments = pd.cut(measurement_data['unix_time'], cut_range)
#print(segments)

#grouped = measurement_data.groupby('label')
#print(type(grouped.mean()))
#print(grouped.mean() , grouped.std())

# R = 10 ^ ((P0-Pi) / gamma)
#xplr-aoa P0= -56.776; gamma= 1.7525
# pi: measurement
#dt.timestamp()
#1657873805.281
#print(dt.timestamp()*1000)
#1657873805281.0
#print(int(dt.timestamp()*1000))
#1657873805281