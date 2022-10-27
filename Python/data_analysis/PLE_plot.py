from math import dist
from re import T
from sqlite3 import Timestamp
from tokenize import group
from typing import final
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
import warnings

warnings.filterwarnings('ignore')

# Listen for incoming datagrams
    
import configparser
from datetime import datetime
# @see usage: https://www.delftstack.com/zh-tw/howto/python/python-ini-file/

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

def get_measurement_data(anchor_config:dict, anchor_name:str, tag_name:str, start_time:int, end_time:int): # time format in second
    try:
        start = datetime.fromtimestamp(start_time)
        end = datetime.fromtimestamp(end_time)
        delta = end - start
    except:
        raise ValueError('Time format error. ')
    
    start_time_ms = start_time * 1000
    end_time_ms = end_time * 1000
    anchor_id = anchor_config[anchor_name]['id']
    tag_id = anchor_config[tag_name]['id']

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
        df = pd.read_sql_query(f"SELECT rssi, channel \
                                 FROM measurement WHERE anchor_id='{anchor_id}' AND instance_id='{tag_id}' \
                                 AND unix_time BETWEEN {start_time_ms} AND {end_time_ms} \
                                 ORDER BY unix_time asc",con = conn)
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

time_list =  [('1', 1662972623), ('4', 1662972688), ('7', 1662972820), ('10', 1662972889),
              ('14', 1662972974), ('22', 1662973126), ('26', 1662973193), ('30', 1662973260),
              ('35', 1662973351), ('40', 1662973447), ('45', 1662973529), ('50', 1662973613)]

final_data = df = pd.DataFrame(data={'tag': ['__tag__'], 'anchor': ['__tag__'], 'distance': [0], \
                                     'rssi': [0], 'channel': [0]})
print(final_data)

for distance, timestamp in time_list:
    print(distance)
    data_A = None
    data_B = None
    data_C = None
    data_D = None
    timestamp5 = timestamp + 5
    timestamp25 = timestamp + 25
    rssi = []
    for query_tag in ['tag-a', 'tag-b']:
        try:
            data_A = get_measurement_data(anchor_config, 'anchor-a', query_tag, timestamp5, timestamp25)
            data_B = get_measurement_data(anchor_config, 'anchor-b', query_tag, timestamp5, timestamp25)
            data_C = get_measurement_data(anchor_config, 'anchor-c', query_tag, timestamp5, timestamp25)
            data_D = get_measurement_data(anchor_config, 'anchor-d', query_tag, timestamp5, timestamp25)
        except ValueError as ex:
            print(f"{ex}")
        
        data_A.insert(0, "distance", [distance]*len(data_A))
        data_A.insert(0, 'anchor', ['anchor-a']*len(data_A))
        data_A.insert(0, 'tag', [ query_tag]*len(data_A))

        data_B.insert(0, "distance", [distance]*len(data_B))
        data_B.insert(0, 'anchor', ['anchor-b']*len(data_B))
        data_B.insert(0, 'tag', [ query_tag]*len(data_B))

        data_C.insert(0, "distance", [distance]*len(data_C))
        data_C.insert(0, 'anchor', ['anchor-c']*len(data_C))
        data_C.insert(0, 'tag', [ query_tag]*len(data_C))

        data_D.insert(0, "distance", [distance]*len(data_D))
        data_D.insert(0, 'anchor', ['anchor-d']*len(data_D))
        data_D.insert(0, 'tag', [ query_tag]*len(data_D))

        final_data = pd.concat([final_data, data_A, data_B, data_C, data_D])
print(final_data)
final_data.to_csv("final_data.csv")