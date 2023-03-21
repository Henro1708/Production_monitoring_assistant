import psycopg2
import time


#Initialization for database
hostname = 'localhost'
database = 'scheduler_times'
username = 'postgres'
pwd = 'W1nter@2023Hydro' #Very safe, isn`t it lol
port_id = 5432


def getPrevTime():
    #create connection to database
    conn = psycopg2.connect(
    host = hostname,
    dbname = database,
    user = username,
    password = pwd,
    port=port_id)
    cur = conn.cursor() #opens cursor (database stuff using psycopg2)
        
    execute="SELECT epoch_time FROM scheduler_times_testing ORDER BY epoch_time DESC LIMIT 1;"

    cur.execute(execute) #executes the thing (idk I copied this from a tutorial and it works)
    result = cur.fetchone()
    print("data fetched")
    cur.close()
    conn.close() #finished database updates
    if result == None:
        return time.time()
    else:
        return result[0]

def databaseUpdate(IP,shift,prevTime):
   #create connection to database
    conn = psycopg2.connect(
    host = hostname,
    dbname = database,
    user = username,
    password = pwd,
    port=port_id)
    timeEpoch = time.time()
    cur = conn.cursor() #opens cursor (database stuff using psycopg2)

                #SQL code \/
    insert_script = 'INSERT INTO scheduler_times_testing(ip_address, epoch_time, time_diff ,shift) VALUES(%s, %s, %s,%s)'
    insert_values = (IP, timeEpoch, timeEpoch-prevTime ,shift)


    cur.execute(insert_script, insert_values) #executes the thing (idk I copied this from a tutorial and it works)
    conn.commit()
    print("Database updated")
    cur.close()
    conn.close() #finished database updates

databaseUpdate(1234,'neveraaa a', getPrevTime())

