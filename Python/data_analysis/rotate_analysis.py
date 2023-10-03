import psycopg2
import warnings ## bypass psycopg2 connection warning
from config import config
import pandas as pd
import socket
import json
import os 
import matplotlib.pyplot as plt
import numpy as np


    
conn = None
cur = None
df = None
analysis = None

start_time = 1658824770000
end_time = 1658824790000

def get_data_aoa(start_time_ms:int, duration_ms:int, anchor_id, tag_id, channel): # time format in ms
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            # read database configuration
            params = config()
            # connect to the PostgreSQL database
            conn = psycopg2.connect(**params)
            conn.autocommit = True
            # create a new cursor
            cur = conn.cursor()
            cur.execute('SELECT version()')
            db_version = cur.fetchone()
            #print(db_version)

            df = pd.read_sql_query(f"SELECT unix_time, azimuth\
            FROM measurement WHERE unix_time BETWEEN {start_time_ms} AND {start_time_ms+duration_ms} \
            AND anchor_id='{anchor_id}' AND instance_id='{tag_id}' AND channel={channel}",con = conn)
            cur.close()
            if conn is not None:
                conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    df = df.set_index('unix_time')
    return df

def get_data(start_time_ms:int, duration_ms:int, anchor_id, tag_id): # time format in ms
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            # read database configuration
            params = config()
            # connect to the PostgreSQL database
            conn = psycopg2.connect(**params)
            conn.autocommit = True
            # create a new cursor
            cur = conn.cursor()
            cur.execute('SELECT version()')
            db_version = cur.fetchone()
            #print(db_version)

            df = pd.read_sql_query(f"SELECT unix_time, azimuth\
            FROM measurement WHERE unix_time BETWEEN {start_time_ms} AND {start_time_ms+duration_ms} \
            AND anchor_id='{anchor_id}' AND instance_id='{tag_id}'",con = conn)
            cur.close()
            if conn is not None:
                conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    df = df.set_index('unix_time')
    return df

time_list =  [('1m',1671951282721),('2m',1671951399238),('3m',1671951511508),('4m',1671951659068),('5m',1671951784018),
              ('6m',1671951926180),('7m',1671952030000),('8m',1671952161364),('9m',1671952268286),('10m',1671952358628),
              ('12m',1671952487163),('15m',1671952602026),('20m',1671952725826),('25m',1671953113912),
              ('30m',1671953630787),('35m',1671953810632),('40m',1671953941682)]
time_list =  [('10m',1671952358628)]

for distance,timestamp in time_list:
    tag_id = '6C1DEBA42193' # tag b
    a_37 = get_data_aoa(timestamp, 60000, '6C1DEBA097F3', tag_id, 37)
    a_38 = get_data_aoa(timestamp, 60000, '6C1DEBA097F3', tag_id, 38)
    a_39 = get_data_aoa(timestamp, 60000, '6C1DEBA097F3', tag_id, 39)
    b_37 = get_data_aoa(timestamp, 60000, '6C1DEBA097FA', tag_id, 37)
    b_38 = get_data_aoa(timestamp, 60000, '6C1DEBA097FA', tag_id, 38)
    b_39 = get_data_aoa(timestamp, 60000, '6C1DEBA097FA', tag_id, 39)
    #c = get_data(timestamp, 60000, 'B8D61A822CAC', tag_id)
    #d = get_data(timestamp, 60000, '24D7EB0B2004', tag_id)

    a_37 = a_37.rename(columns={'azimuth': "a_37"})
    a_38 = a_38.rename(columns={'azimuth': "a_38"})
    a_39 = a_39.rename(columns={'azimuth': "a_39"})
    b_37 = b_37.rename(columns={'azimuth': "b_37"})
    b_38 = b_38.rename(columns={'azimuth': "b_38"})
    b_39 = b_39.rename(columns={'azimuth': "b_39"})
    #c = c.rename(columns={'azimuth': "c"})
    #d = d.rename(columns={'azimuth': "d"})

    result_a = a_37.join([a_38, a_39], how='outer')
    result_a = result_a.sort_index()
    result_a = result_a.interpolate(method='linear')
    result_a['a'] = result_a.mean(axis=1)
    result_a = result_a.drop(columns=['a_37', 'a_38', 'a_39'])
    
    result_b = b_37.join([b_38, b_39], how='outer')
    result_b = result_b.sort_index()
    result_b = result_b.interpolate(method='linear')
    result_b['b'] = result_b.mean(axis=1)
    result_b = result_b.drop(columns=['b_37', 'b_38', 'b_39'])

    result = result_a.join([result_b], how='outer')
    result = result.sort_index()
    result = result.interpolate(method='linear')
    result = result.groupby(np.arange(1671952358000, 1671952418000, 1000)).mean()
    print(result)

    #merge
    '''for rssi
    #result = a_37.join([a_38, a_39, b_37, b_38, b_39], how='outer')
    result = a_37.join([a_38, a_39, b_37, b_38, b_39], how='outer')
    result = result.sort_index()
    result = result.interpolate(method='linear')
    print(result)
    '''

    chart = result.plot(title='Fixed distance Tag rotation ' + distance,  #圖表標題
                    xlabel='timestamp',
                    ylabel='Azimuth(angle)',
                    ylim=(-20, 20),
                    grid=True,
                    legend=(True),
                    figsize=(10, 5))
    #plt.show()
    plt.legend(loc='upper left')
    plt.savefig(distance + '(azimuth).png')

    #os.system('pause')
 


