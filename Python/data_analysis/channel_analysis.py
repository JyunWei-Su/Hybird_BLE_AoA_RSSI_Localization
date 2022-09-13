import psycopg2
from config import config
import pandas as pd
import socket
import json
import os 
import matplotlib.pyplot as plt


    
conn = None
cur = None
df = None
analysis = None

start_time = 1658824770000
end_time = 1658824790000
try:
    # read database configuration
    params = config()
    # connect to the PostgreSQL database
    conn = psycopg2.connect(**params)
    conn.autocommit = True
    # create a new cursor
    cur = conn.cursor()
    cur.execute('SELECT version()')
    db_version = cur.fetchone()
    print(db_version)

    df = pd.read_sql_query(f"SELECT rssi, channel FROM measurement WHERE anchor_id='6C1DEBA097FA' AND unix_time BETWEEN {start_time} AND {end_time};",con=conn)
    print(df)
    #df.groupby(['rssi'])
    #print(df)
    #@see how to group by: https://ithelp.ithome.com.tw/articles/10274207
    analysis = df.groupby(['channel', 'rssi']).size().reset_index(name="count")
    print(analysis)
    cur.close()
    if conn is not None:
        conn.close()
    
    # execute the INSERT statement

except (Exception, psycopg2.DatabaseError) as error:
    print(error)


#rows = (df['年別'] == 2019) & (df['縣市別'] == '臺北市')
#columns = ['細分', '1月', '2月', '3月']
#result = df.loc[rows, columns].head(10)
#result.set_index('細分', inplace=True)
channel_37 = analysis[analysis['channel'] == 37].drop(columns=['channel']).rename(columns = {'count':'CH37'})
channel_38 = analysis[analysis['channel'] == 38].drop(columns=['channel']).rename(columns = {'count':'CH38'})
channel_39 = analysis[analysis['channel'] == 39].drop(columns=['channel']).rename(columns = {'count':'CH39'})

print(channel_37)
analysis = channel_37.merge(channel_38, on='rssi', how='outer').merge(channel_39, on='rssi', how='outer')
analysis = analysis.set_index('rssi')
analysis = analysis.reindex(pd.RangeIndex(-40, -80, -1)).fillna(0)
print(analysis)
 
chart = analysis.plot(title='Channel Analysis',  #圖表標題
                    xlabel='rssi(dbm)',
                    ylabel='Count',
                    legend=True,
                    figsize=(10, 5))
plt.show()

