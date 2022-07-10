import psycopg2
from config import config
import socket
import json

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
print(s.getsockname()[0])
localIP     = s.getsockname()[0]
s.close()

localPort   = 4102
bufferSize  = 1024

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# Bind to address and ip

UDPServerSocket.bind((localIP, localPort))
print("UDP server up and listening")

# Listen for incoming datagrams
    
conn = None
cur = None
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

while(True):
    try:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        message = bytesAddressPair[0]

        address = bytesAddressPair[1]

        clientMsg = "Message from Client:{}".format(message)
        clientIP  = "Client IP Address:{}".format(address)
        obj = json.loads(message)
        print("=============================================")
        #print(clientMsg)
        #print(clientIP)
        print(obj)
        #anchor_type = obj['type']
        #unix_time = obj['unix_time']
        #uudf_time = obj['uudf_time']
        print("********************************************")
        sql = """INSERT INTO measurement
                VALUES ('{anchor_type}',{unix_time},{uudf_time},
                '01234567890a','987654321abc',-30,10,20,37, 'hello-world');"""\
                .format(anchor_type = obj['type'], unix_time = obj['unix_time'], uudf_time = obj['uudf_time'])
        print("--------------------------------------------")
        #sql = sql.replace(':', '')
        print(sql)
        cur.execute(sql)
        # commit the changes to the database
        #conn.commit() # because conn haved set to autocommit, no longer to use this
                        # @see https://www.postgresqltutorial.com/postgresql-python/transaction/ 
        # close communication with the database
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
cur.close()
if conn is not None:
    conn.close()