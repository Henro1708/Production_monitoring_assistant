import time
from datetime import datetime
from pylogix import PLC
from plc import station
import json
import psycopg2

#STARTS station     
JLLong = station("JLLONG")  # Station End of line OP100
JLLongIpAdd = JLLong.selectIP()

#Initialization for database
hostname = 'localhost'
database = 'scheduler_times'
username = 'postgres'
pwd = 'W1nter@2023Hydro' #Very safe, isn`t it lol
port_id = 5432


def checkPart():    # main function that checks when a part is made and how long it took
    t = time.time()
    t2 = time.time()
    timeNow = datetime.now()

    while JLLong.onePart()[0][3] == 1:  # These two lines are to make sure we don`t get 2 positives from the same part (because they are on the same loop)`
        pass

    while timeNow.strftime("%H:%M") !=endTime:  # makes sure the loop isnt infinite
        
        if JLLong.onePart()[0][3] == 1:
            print("Part made! Made in: " + str(round(t2-t,1)) + " sec")

            print(str(JLLong.prodCounter()[0][3]) + " parts on this shift")
            return True, datetime.now()
        t2 = time.time()
        timeNow = datetime.now()
    return False, datetime.now()

def whichShift(time):       # Tells which shift we are in and when it will end
    
    if time >= 7 and time < 15:
        #print("day shift")
        return "day" , "14:59"    
    elif time >= 15 and time < 23:
        #print("afternoon shift")                    
        return "afternoon", "22:59"
    elif time  >= 23 or time < 7:
        #print("night shift")
        return "night" , "06:59"
    else:
        print("Mid of shift")
        return "none" , "0"
    

def getPrevTime():
    #create connection to database
    conn = psycopg2.connect(
    host = hostname,
    dbname = database,
    user = username,
    password = pwd,
    port=port_id)
    cur = conn.cursor() #opens cursor (database stuff using psycopg2)
        
    execute="SELECT epoch_time FROM scheduler_times_table WHERE ip_address='10.10.16.132' ORDER BY epoch_time DESC LIMIT 1;"

    cur.execute(execute) #executes the thing (idk I copied this from a tutorial and it works)
    result = cur.fetchone()
    #print("data fetched")
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
    insert_script = 'INSERT INTO scheduler_times_table(ip_address, epoch_time, time_diff ,shift) VALUES(%s, %s, %s,%s)'
    insert_values = (IP, timeEpoch, timeEpoch-prevTime ,shift)


    cur.execute(insert_script, insert_values) #executes the thing (idk I copied this from a tutorial and it works)
    conn.commit()
    #print("Database updated")
    cur.close()
    conn.close() #finished database updates
    return timeEpoch


# MAIN ## MAIN ## MAIN ## MAIN ## MAIN ## MAIN ## MAIN ## MAIN ## MAIN ## MAIN ## MAIN ## MAIN ## MAIN ## MAIN ## MAIN ## MAIN ## MAIN ## MAIN #

while True:
    now = datetime.now()
    nowTime = now.strftime("%H")
    shift, endTime = whichShift(int(nowTime))
    print(shift)
    while now.strftime("%H:%M") !=endTime:   #START CHECKING EVERY MOMENT
        if endTime == '0':
            break 
        
        pMde, timePart = checkPart()
        if pMde == True: #If a part is made, we check if it was over the cycletime and by how much
                lastCycle = getPrevTime()   # gets the last time a part was made for the calculations
                databaseUpdate(JLLongIpAdd,shift,lastCycle) # saves the timestamp on a database
        now = datetime.now()
    print("END OF SHIFT")
    while now.strftime("%H") != '07' or '15' or '23':
        now = datetime.now()