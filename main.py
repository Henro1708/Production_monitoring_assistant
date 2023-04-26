import time
from datetime import datetime
from pylogix import PLC
from plc import station
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import pandas as pd
import numpy as np
from openpyxl.styles import Font, Color, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl import Workbook
import psycopg2
import xlwings as xw




# !MAIN ##### !MAIN ##### !MAIN ##### !MAIN ##### !MAIN ##### !MAIN ##### !MAIN ##### !MAIN ##### !MAIN ##### !MAIN ##### !MAIN ##### !MAIN ####

#Checking start time and assigning an appropriate shitft length

def firstHour(targetStation):               # Checks if a part is made on the first hour 
    try:
        
        t1 = time.time()
        t2 = time.time()
        while (t1 - t2) < 3600:   #seconds in an hour
            if bool(targetStation.onePart()[0][3]) == 1:          #PLC says a part is made  
                print("First part made! (First hour): {}".format(targetStation))
                return True
            t1=time.time()
        return False
    except:
        print("socket fail {}".format(targetStation))
        return False

def afterAnHour(endTime, targetStation): # checks the time a part takes to be made after the first hour
    try:
        t1 = time.time()
        t2 = time.time()
        while bool(targetStation.onePart)()[0][3] != 1: #PLC tells when part is made
            
            timeNow = datetime.now()
            if timeNow.strftime("%H:%M") == endTime:   # If it is not the end of the shift, keep checking until a part is made
                return False,0
            t2 = time.time()
        print("Part made! (Not first hour): {}".format(targetStation))
        return True, (t2-t1)
    except:
        print("socket fail {}".format(targetStation))
        return False,0





def checkPart(endTime,breakPeriod,lunchTime,targetStation):    # main function that checks when a part is made and how long it took
    try:
        t = time.time()
        t2 = time.time()
        timeNow = datetime.now()

        while bool(targetStation.onePart()[0][3]) == 1:  # These two lines are to make sure we don`t get 2 positives from the same part (because they are on the same loop)`
            pass

        while timeNow.strftime("%H:%M") != endTime:  # makes sure the loop isnt infinite
            if timeNow.strftime("%H:%M") == breakPeriod or timeNow.strftime("%H:%M") == lunchTime:
                return False, 1
            if bool(targetStation.onePart()[0][3]) == 1:  
                print("Part made! Made in: " + str(round(t2-t,1)) + " sec: "+ str(targetStation))

                print(str(targetStation.prodCounter()[0][3]) + " parts on this shift")   # When a part is made we return True and the time it took
                return True, t2-t
            
            t2 = time.time()
            timeNow = datetime.now()
        return False, 0
    except:
        print("socket fail {}".format(targetStation))
        return False,1


def whichShift(time, endArr, breakArr, lunchArr,hourArr):       # Tells which shift we are in and when it will end
    
    if time >= hourArr[0] and time < hourArr[1]:   # These values are passed as parameters from the other file (run.py)
        print("day shift")
        return "day" , endArr[0] , breakArr[0], lunchArr[0]     
    elif time >= hourArr[1] and time < hourArr[2]:
        print("afternoon shift")                    
        return "afternoon", endArr[1] , breakArr[1] , lunchArr[1]  
    elif time  >= hourArr[2] or time < hourArr[0]:
        print("night shift")
        return "night" , endArr[2] , breakArr[2] , lunchArr[2] 
    else:
        print("Mid of shift")
        return "none" , "0"
    
def inFirstHour(hour, hourArr):  # True when we are at the beginning of a shift
    
    if int(hour) == hourArr[0]:  # Values come from run.py as parameters
        return True
    elif int(hour) == hourArr[1]:
        return True
    elif int(hour) == hourArr[2]:
        return True
    else: 
        return False    
    
def breakTime(timee,breakPeriod,lunchTime):  #called timee so it doesn't get messed up with the library
    if timee == breakPeriod:
        time.sleep(10*60)
        return True
    if timee == lunchTime:    # If it is break time we pause and only resume after the break/lunch has ended
        time.sleep(20*60)
        return True
    else:
        return False

def getPrevTime(hostname,database,username,pwd,port_id,stationIP):
    #create connection to database
    conn = psycopg2.connect(
    host = hostname,
    dbname = database,
    user = username,
    password = pwd,
    port=port_id)
    cur = conn.cursor() #opens cursor (database stuff using psycopg2)
        #SQL code
    execute="SELECT epoch_time FROM parts_timestamp WHERE ip_address='{}' ORDER BY epoch_time DESC LIMIT 1;".format(stationIP)

    cur.execute(execute) #executes the thing 
    result = cur.fetchone()
    
    cur.close()
    conn.close() #finished database fetch
    if result == None:
        return time.time()
    else:
        return result[0]



def databaseUpdate(IP,shift,prevTime,hostname,database,username,pwd,port_id):
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
    insert_script = 'INSERT INTO parts_timestamp(ip_address, epoch_time, time_diff ,shift) VALUES(%s, %s, %s,%s)'
    insert_values = (IP, timeEpoch, timeEpoch-prevTime ,shift)


    cur.execute(insert_script, insert_values) #executes query
    conn.commit()
    #print("Database updated")
    cur.close()
    conn.close() #finished database updates
    return timeEpoch  # Returns the value we just fetched

def findStation(sht,STATION):  # Loops through the excel file and finds which row has the expected station
    for i in range(5,64):
        if sht['C{}'.format(i)].value == STATION:
            return i #returns the row
    

def getCycleTime(targetstat):
    with xw.App() as app:
        timeNow = datetime.now()
        weekDay = timeNow.date().weekday() # 0 = Monday...
        wb = xw.Book(r"workingTable\shifts_table.xlsx") #opens the workbook on excel

        if weekDay == 0: # finds out which day of the week it is and opens the correct sheet
            sht = wb.sheets['Mon']
        elif weekDay == 1:
            sht = wb.sheets['Tue']
        elif weekDay == 2:
            sht = wb.sheets['Wed']  
        elif weekDay == 3:
            sht = wb.sheets['Thu']
        elif weekDay == 4:
            sht = wb.sheets['Fri']
        elif weekDay == 5:
            sht = wb.sheets['Sat']
        elif weekDay == 6:
            sht = wb.sheets['Sun']
        index = findStation(sht,targetstat)
        CYCLETIME = sht['G{}'.format(index)].value  # sec/part decided on the excel file 

        wb.close()
    
    return CYCLETIME

def excelWrite(shift, targetstat, shiftLength, time_awarded, nOfParts, nOfMicro, nOfMajor, timeMicro, timeMajor):
    with xw.App() as app:
        timeNow = datetime.now()
        weekDay = timeNow.date().weekday() # 0 = Monday...
        if shift == "night":
            if weekDay == 0:
                weekDay =6
            else:
                weekDay -=1



            
        wb = xw.Book(r"workingTable\shifts_table.xlsx", read_only= False) #opens the workbook on excel


        if weekDay == 0: # finds out which day of the week it is and opens the correct sheet
            sht = wb.sheets['Mon']
        elif weekDay == 1:
            sht = wb.sheets['Tue']
        elif weekDay == 2:
            sht = wb.sheets['Wed']  
        elif weekDay == 3:
            sht = wb.sheets['Thu']
        elif weekDay == 4:
            sht = wb.sheets['Fri']
        elif weekDay == 5:
            sht = wb.sheets['Sat']
        elif weekDay == 6:
            sht = wb.sheets['Sun']
        index = findStation(sht,targetstat) # finds the row we will be edditing based on the station we are monitoring
        if shift == "afternoon":
            index+=1
        elif shift == "night":
            index+=2

        sht['D{}'.format(index)].value = shiftLength/3600 # The original value was in seconds, so we transfer it into hours
        sht['E{}'.format(index)].value = time_awarded/3600
        sht['H{}'.format(index)].value = nOfParts
        sht['L{}'.format(index)].value = nOfMicro
        sht['O{}'.format(index)].value = nOfMajor
        sht['N{}'.format(index)].value = timeMicro/3600
        sht['Q{}'.format(index)].value = timeMajor/3600

        wb.save(r"workingTable\shifts_table.xlsx")
        wb.close()
        


# MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ####



def main(targetstat, endArr, breakArr, lunchArr,hourArr): #parameters are station, end times for all shifts as an array, break times, lunchtimes, and shift start times (arrays)
    # Setup
    

    #STARTS station     
    targetStation = station(targetstat)  # Station End of line OP100
    stationIP = targetStation.selectIP()

    #Initialization for database
    hostname = '10.110.19.205' # IP address of the server laptop
    database = 'timestamp'
    username = 'postgres'
    pwd = 'W1nter@2023Hydro' #Very safe, I know
    port_id = 5432

    SEC_HOURS = 3600
    print("Program running: " + targetstat)
    
    
    while True:             # BEGINNING OF SHIFT ## BEGINNING OF SHIFT ## BEGINNING OF SHIFT ## BEGINNING OF SHIFT #

        resAfterAnHour = False
        happenedInFirst = False

        majorBucket=[]  # Resets all the overtime categories #Arrays of incidents greater than 3 minutes
        
        microBucket = [] #similar but less than 3 mins
        
        now = datetime.now()
        nowTime = now.strftime("%H")
        
        while inFirstHour(nowTime, hourArr) == False:   #this waits for the next full shift to start
            now = datetime.now()
            nowTime = now.strftime("%H")
        #print("in shift")

        shift, endTime , breakPeriod, lunchTime  = whichShift(int(nowTime),endArr,breakArr,lunchArr,hourArr)  #finds out which shift it is
        happenedInFirst = firstHour(targetStation) #returns a bool that indicates whether production was started in the first hour of the shift or not
        if happenedInFirst == True:   # Tests for the first hour (anytime in the first hour counts as a full shift worked)
            shiftLength = (7.5 * SEC_HOURS)   # 8h - break times
            lastCycle = getPrevTime(hostname,database,username,pwd,port_id,stationIP) #fetches the database for the previous time a part was made
            databaseUpdate(stationIP,shift,lastCycle,hostname,database,username,pwd,port_id) #updates the database every time a part is made

        else:
            try:
                resAfterAnHour,timeUsed = afterAnHour(endTime,targetStation)   #if production was not strarted in the first hour, it checks when a part is made or iof the shift is over
                if resAfterAnHour == True: #if a part was made
                    shiftLength = (6.5*SEC_HOURS) - timeUsed #this determines the amount of time worked on the shift
                    lastCycle = getPrevTime(hostname,database,username,pwd,port_id,stationIP) #refer to 208
                    databaseUpdate(stationIP,shift,lastCycle,hostname,database,username,pwd,port_id)
                else:
                    shiftLength = 0 #DID NOT RUN 
            except:
                resAfterAnHour,timeUsed = afterAnHour(endTime,targetStation)   #if production was not strarted in the first hour, it checks when a part is made or iof the shift is over
                if resAfterAnHour == True: #if a part was made
                    shiftLength = (6.5*SEC_HOURS) - timeUsed #this determines the amount of time worked on the shift
                    lastCycle = getPrevTime(hostname,database,username,pwd,port_id,stationIP) #refer to 208
                    databaseUpdate(stationIP,shift,lastCycle,hostname,database,username,pwd,port_id)
                else:
                    shiftLength = 0 #DID NOT RUN
      
        CYCLETIME = getCycleTime(targetstat)
        
        # MAIN PART OF SHIFT ## MAIN PART OF SHIFT ## MAIN PART OF SHIFT ## MAIN PART OF SHIFT ## MAIN PART OF SHIFT ## MAIN PART OF SHIFT #

        while now.strftime("%H:%M") != endTime:   #START CHECKING EVERY MOMENT
            try:
                pMde, timePerPart = checkPart(endTime,breakPeriod,lunchTime, targetStation) #calls function to check parts
                if pMde == False and timePerPart == 1:
                    now = datetime.now()
                    breakTime(now.strftime("%H:%M"),breakPeriod,lunchTime) 
                    parts, timing = afterAnHour(endTime,targetStation)
                    
                if pMde == True: #If a part is made, we check if it was over the cycletime and by how much
                    lastCycle = getPrevTime(hostname,database,username,pwd,port_id,stationIP)   # gets the last time a part was made for the calculations
                    databaseUpdate(stationIP,shift,lastCycle,hostname,database,username,pwd,port_id) # saves the timestamp on a database
                    if timePerPart > CYCLETIME:
                        if timePerPart - CYCLETIME > 3 *60: # over 3 min = Service
                            print("Major problem at: "+ str(now))
                            majorBucket.append(timePerPart-CYCLETIME)
                                            
                        else:                                   # Less than 3 min = micro
                            print("Micro problem at: "+ str(now))
                            microBucket.append(timePerPart-CYCLETIME)
            except:
                pass
                        

            now = datetime.now()
        print("END OF SHIFT "+ str(targetstat))
        # END OF SHIFT HERE #### END OF SHIFT HERE #### END OF SHIFT HERE #### END OF SHIFT HERE #### END OF SHIFT HERE #### END OF SHIFT HERE ###
        
        nOfParts = targetStation.prodCounter()[0][3]
        if nOfParts == None:
            nOfParts = 0
        time_awarded = nOfParts * CYCLETIME  #How much time was actually produced on this shift
        
        
        nOfMajor = len(majorBucket)  # Number of late parts occurances
        nOfMicro = len(microBucket)
        
        timeMicro = 0
        timeMajor = 0

        for i in range(0, nOfMicro):    # Counts the total time used on these occurances
            timeMicro = timeMicro + microBucket[i]   
        
        for i in range(0, nOfMajor):    
            timeMajor = timeMajor + majorBucket[i]

        # WRITING IN EXCEL ## WRITING IN EXCEL ## WRITING IN EXCEL ## WRITING IN EXCEL #
        
        excelWrite(shift, targetstat, shiftLength, time_awarded, nOfParts, nOfMicro, nOfMajor, timeMicro, timeMajor)
        



