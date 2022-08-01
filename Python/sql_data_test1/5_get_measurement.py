from re import T
from tokenize import group
import psycopg2
from config import config
import pandas as pd
import numpy as np
import socket
import json
import os 

# Listen for incoming datagrams
    
import configparser
from datetime import datetime
# @see usage: https://www.delftstack.com/zh-tw/howto/python/python-ini-file/

#filename = "anchor.ini"


def get_anchor_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    config_dict = config._sections
    for anchor in [section for section in config.sections() if 'anchor' in section]:
        for key in ['coordinate', 'norm_vector', 'anim_vector', 'elev_vector', 'const']:
            config_dict[anchor][key] = eval(config_dict[anchor][key])
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
                                 FROM measurement WHERE anchor_id='{id}' AND instance_id='6C1DEBA41680' \
                                 AND unix_time BETWEEN {start_time_ms} AND {end_time_ms} \
                                 ORDER BY unix_time asc",con = conn)
        # or SELECT * FROM measurement WHERE anchor_id='6C1DEBA097FA' AND to_timestamp(unix_time::double precision /1000) BETWEEN timestamp '2022-07-14 23:28:20.000' AND timestamp '2022-07-15 23:28:30.000';
        print(df)
        #os.system('pause')
        cur.close()
        if conn is not None:
            conn.close()
        # execute the INSERT statement

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    return df


anchor_config = get_anchor_config("anchor.ini")
print(anchor_config)

measurement_data = None
try:
    measurement_data = get_measurement_data(anchor_config, 'anchor-b', 1657825678, 1657856078)
except ValueError as ex:
    print(f"{ex}")
measurement_data['label'] = measurement_data['unix_time'] // 1000 # 如果要切更細??
print(measurement_data)
measurement_data.drop(columns='unix_time', inplace=True) 
measurement_data = measurement_data[['label','rssi','azimuth','elevation']] #swap order
#cut_range = np.arange(1657845678000, 1657845878000, 1000)
#segments = pd.cut(measurement_data['unix_time'], cut_range)
#print(segments)
grouped = measurement_data.groupby('label')
print(type(grouped.mean()))
print(grouped.mean() , grouped.std())

# R = 10 ^ ((P0-Pi) / gamma)
#xplr-aoa P0= -56.776; gamma= 1.7525
# pi: measurement
#dt.timestamp()
#1657873805.281
#print(dt.timestamp()*1000)
#1657873805281.0
#print(int(dt.timestamp()*1000))
#1657873805281