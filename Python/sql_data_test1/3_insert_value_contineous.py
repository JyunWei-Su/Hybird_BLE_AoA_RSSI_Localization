import psycopg2
from config import config
import socket
import select
import json

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
print(s.getsockname()[0])
localIP     = s.getsockname()[0]
s.close()

# https://github.com/aseempurohit/udp-server-multiple-ports/blob/master/udp-server.py
localPort   = [4101, 4102]
bufferSize  = 1024
UDPServerSockets = []

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# Bind to address and ip

for port in localPort:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((localIP, port))
    UDPServerSockets.append(server_socket)
print("UDP server up and listening at ", localPort)

# Listen for incoming datagrams
    
conn = None
cur = None
#連線資料庫
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
    # execute the INSERT statement

except (Exception, psycopg2.DatabaseError) as error:
    print(error)

#聽port
while(True):
    try:
        readable, writable, exceptional = select.select(UDPServerSockets, [], [])
        for s in readable:

            message, address = s.recvfrom(bufferSize)

            clientMsg = "Message from Client:{}".format(message)
            clientIP  = "Client IP Address:{}".format(address)

            obj = json.loads(message) #轉成dict
            print("=============================================")
            #print(clientMsg)
            #print(clientIP)
            print(obj)
            #anchor_type = obj['type']
            #unix_time = obj['unix_time']
            #uudf_time = obj['uudf_time']
            sql = None
            if(obj['type'] == 'rssi+aoa:xplr-aoa' and obj['data'] == 'measurement'):
                sql = """INSERT INTO measurement (anchor_type, unix_time, uudf_time,
                        instance_id, anchor_id, rssi, azimuth, elevation, channel)
                        VALUES ('{type}',{unix_time},{uudf_time},
                        '{instance_id}', '{anchor_id}', {rssi}, {azimuth}, {elevation}, {channel});"""\
                        .format_map(obj)
                print(sql)
                cur.execute(sql)
            elif(obj['type'] == 'rssi:esp32' and obj['data'] == 'measurement'):
                sql = """INSERT INTO measurement (anchor_type, unix_time, uudf_time,
                        instance_id, anchor_id, rssi)
                        VALUES ('{type}',{unix_time},{uudf_time},
                        '{instance_id}', '{anchor_id}', {rssi});"""\
                        .format_map(obj)
                print(sql)
                cur.execute(sql)
            print("--------------------------------------------")

            # commit the changes to the database
            #conn.commit() # because conn haved set to autocommit, no longer to use this
                            # @see https://www.postgresqltutorial.com/postgresql-python/transaction/ 
            # close communication with the database
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
cur.close()
if conn is not None:
    conn.close()