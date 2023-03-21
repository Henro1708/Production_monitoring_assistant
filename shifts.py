import time
from datetime import datetime
from pylogix import PLC
from plc import station
import json
import psycopg2
import pandas as pd



#Import table
tb = pd.read_excel("./table_shifts.xlsx")


fiveMin = 5*60
sInAnHour = 3600


partMade = 1   #FUnction when part is made (last robot is active)
partsDone =0    # Function that gives the number of parts made


def firstHour():                    
    t1 = time.time()
    t2 = time.time()
    while (t1 - t2) < sInAnHour:   #seconds in an hour
        if partMade == 1:          #PLC says a part is made
               
            return True
        t1=time.time()
    return False

def afterAnHour():
    t1 = time.time()
    t2 = time.time()
    while partMade != 1: #PLC tells when part is made
        t2 = time.time()
        timeNow = datetime.now()
        if int(timeNow.strftime("%H")) ==endTime:
            return False,0
        time.sleep(0.05)  #This might need to be removed
    return True, (t2-t1)


def checkPart():
    t = time.time()
    t2 = time.time()
    timeNow = datetime.now()
    while int(timeNow.strftime("%H")) !=endTime:  
        timeNow = datetime.now()
        if partMade == 1:
            return True, t2-t
        t2 = time.time()
    return False, 0
        
    
def whichShift(time):
    
    if time == 6:
        print("day shift")
        return "day" , 14
    elif time == 14:
        print("afternoon shift")
        return "afternoon", 22
    elif time  == 22:
        print("night shift")
        return "night" , 6
    else:
        print("none")
        return "none" , 0
    
def inShift(hour):
    if int(hour) == 6 or 14 or 22:
        return True
    else: 
        return False

#MAIN #### MAIN #### MAIN ####### MAIN ######## MAIN ######### MAIN ###### MAIN ####### MAIN ######### MAIN ############# MAIN ####

majorBucket=[]
majorMoment = []
minorBucket=[]
minorMoment = []
microBucket = []
microMoment = []

#initialization of station


#Initialization for database
hostname = 'localhost'
database = 'scheduler_times'
username = 'postgres'
pwd = 'W1nter@2023Hydro' #Very safe, isn`t it lol
port_id = 5432

while True:
    CYCLETIME = int(tb.iat[1,0])  # sec/part

    conn = psycopg2.connect(
    host = hostname,
    dbname = database,
    user = username,
    password = pwd,
    port=port_id)



    now = datetime.now()
    nowTime = now.strftime("%H")
    while not inShift(nowTime):
        now = datetime.now()
        nowTime = now.strftime("%H")
        print(nowTime)
    print("in shift")
    shift, endTime = whichShift(int(nowTime)) 

    if firstHour() == True:
        shiftLength = 8 * sInAnHour

        #partsDone +=1

    else:
        res,timeUsed = afterAnHour()
        if res == True:
            #partsDone +=1

            shiftLength = (7*sInAnHour) - timeUsed

        else:
            shiftLength = 0 #DID NOT RUN
    
    while int(now.strftime("%H")) !=endTime:   #START CHECKING EVERY MOMENT
        pMde, timePerPart = checkPart() #calls function to check parts
        
        if pMde == True:
            #partsDone +=1
            if timePerPart > CYCLETIME:
                if timePerPart - CYCLETIME > fiveMin: # over 5 min = major
                    majorBucket.append(timePerPart)
                    majorMoment.append(time.time())
                elif timePerPart- CYCLETIME > 1*60:  #one minute = minor
                    minorBucket.append(timePerPart)
                    minorMoment.append(time.time())
                else:                                   # Less than a min = micro
                    microBucket.append(timePerPart)
                    microMoment.append(time.time())
        else: 
            majorBucket.append(timePerPart)  #DID NOT MAKE A PART ANYMORE UNTIL END OF SHIFT
            majorMoment.append(time.time())

        now = datetime.now()
    # END OF SHIFT HERE ####################################################

    time_awarded = partsDone * CYCLETIME  #How much time was actually produced on this shift
    timeDiff = time_awarded - shiftLength
    nOfMinor = len(minorBucket)
    nOfMajor = len(majorBucket)
    nofMicro = len(microBucket)

    cur = conn.cursor() #opens cursor (database stuff using psycopg2)

                #SQL code \/
    insert_script = 'INSERT INTO shift_monitoring(date, shift, hours_worked, hours_earned,hours_diff, n_of_micro, n_of_minor, n_of_major) VALUES(current_timestamp, %s,%s,%s,%s,%s,%s,%s)'
    insert_values = (shift, shiftLength, time_awarded,timeDiff, nofMicro,nOfMinor, nOfMajor)


    cur.execute(insert_script, insert_values) #executes the thing (idk I copied this from a tutorial and it works)
    conn.commit()
    print("Database updated")
    cur.close()
    conn.close() #finished database updates
