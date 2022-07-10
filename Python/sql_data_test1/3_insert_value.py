import psycopg2
from config import config

def insert_data(anchor_type = None,
                unix_time = None, uudf_time = None,
                instance_id = None, anchor_id = None,
                rssi = None, azimuth = None, elevation = None,
                channel = None, message = None):
    """INSERT INTO measurement
             VALUES ('rssi+aoa',99999,67890,'01234567890a','987654321abc',-30,10,20,37, 'hello');"""
    sql = f"""INSERT INTO measurement
             VALUES('{anchor_type}',{unix_time},{uudf_time},
                    '{instance_id}','{anchor_id}',
                    {rssi},{azimuth},{elevation},
                    {channel},'{message}');"""
    sql = sql.replace(",'None'", '')
    sql = sql.replace(",None", '')
    print(sql)
    conn = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        cur.execute('SELECT version()')
        db_version = cur.fetchone()
        print(db_version)
        # execute the INSERT statement
        cur.execute(sql)
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    # insert one vendor
    insert_data(anchor_type='rssi+aoa',
                unix_time=88888, uudf_time=6666666,
                instance_id='01234567890a', anchor_id='987654321abc',
                rssi=-30, azimuth=10,
                channel=37)