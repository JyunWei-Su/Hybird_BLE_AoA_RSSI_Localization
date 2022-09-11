from re import T
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


anchor_config = get_system_config("system.ini")
#pp.pprint(anchor_config)

measurement_data = None
try:
    measurement_data = get_measurement_data(anchor_config, 'anchor-a', 1662611421, 1662611441)
except ValueError as ex:
    print(f"{ex}")
#print(measurement_data)
measurement_data['label'] = measurement_data['unix_time'] // 1000 # 如果要切更細??
measurement_data.drop(columns='unix_time', inplace=True) 
measurement_data = measurement_data[['label','rssi','azimuth','elevation']] #swap order

angle = '-80'
mean = measurement_data['elevation'].mean()
error = int(angle) - mean
fig, ax = plt.subplots()
fig.set_size_inches(8,2.5)
ax.clear()
ax.set_title(angle + '°')
ax.set_xlim([-90,90])
ax.set_ylim([0, 1])
ax.text(-80,0.9,s = ('error = %.2f' %error),fontsize = 14)
#plt.axvline(x = angle,color = 'lawngreen')
plt.axvline(x = mean,color = 'red')
sns.histplot(data = measurement_data['elevation'], stat="density", ax = ax)
plt.savefig('result_0908/elevation_' + angle + '°.png' )
plt.pause(3)
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