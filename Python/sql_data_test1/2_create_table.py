import psycopg2
from config import config


def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = [
        """
        CREATE TABLE measurement (
            anchor_type VARCHAR(32) NOT NULL,
            unix_time   BIGINT NOT NULL,
            uudf_time   BIGINT NOT NULL,
            instance_id CHAR(12) NOT NULL,
            anchor_id   CHAR(12) NOT NULL,
            rssi        INTEGER,
            azimuth     INTEGER,
            elevation   INTEGER,
            channel     INTEGER,
            message     VARCHAR(128)
        )
        """]
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute('SELECT version()')
        db_version = cur.fetchone()
        print(db_version)
        # create table one by one
        
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    create_tables()