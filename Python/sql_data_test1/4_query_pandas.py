import psycopg2
from config import config
import pandas as pd
import socket
import json
import os 



# Listen for incoming datagrams
    
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
    cur.execute('SELECT version()')
    db_version = cur.fetchone()
    print(db_version)

    # https://stackoverflow.com/questions/27884268/return-pandas-dataframe-from-postgresql-query-with-sqlalchemy
    df = pd.read_sql_query('select * from "measurement"',con=conn)
    print(df)
    os.system('pause')
    cur.close()
    if conn is not None:
        conn.close()
    
    # execute the INSERT statement

except (Exception, psycopg2.DatabaseError) as error:
    print(error)

