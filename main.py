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
    t1 = time.time()
    t2 = time.time()
    while (t1 - t2) < 3600:   #seconds in an hour
        if targetStation.onePart()[0][3] == 1:          #PLC says a part is made  
            print("First part made! (First hour)")
            return True
        t1=time.time()
    return False


def afterAnHour(endTime, targetStation): # checks the time a part takes to be made after the first hour
    t1 = time.time()
    t2 = time.time()
    while targetStation.onePart()[0][3] != 1: #PLC tells when part is made
        
        timeNow = datetime.now()
        if timeNow.strftime("%H:%M") == endTime:
            return False,0
        t2 = time.time()
    print("Part made! (Not first hour)")
    return True, (t2-t1)





def checkPart(endTime,breakPeriod,lunchTime,targetStation):    # main function that checks when a part is made and how long it took
    t = time.time()
    t2 = time.time()
    timeNow = datetime.now()

    while targetStation.onePart()[0][3] == 1:  # These two lines are to make sure we don`t get 2 positives from the same part (because they are on the same loop)`
        pass

    while timeNow.strftime("%H:%M") != endTime:  # makes sure the loop isnt infinite
        if timeNow.strftime("%H:%M") == breakPeriod or timeNow.strftime("%H:%M") == lunchTime:
            return False, 1
        if targetStation.onePart()[0][3] == 1:
            print("Part made! Made in: " + str(round(t2-t,1)) + " sec")

            print(str(targetStation.prodCounter()[0][3]) + " parts on this shift")
            return True, t2-t
        
        t2 = time.time()
        timeNow = datetime.now()
    return False, 0


def whichShift(time, endArr, breakArr, lunchArr,hourArr):       # Tells which shift we are in and when it will end
    
    if time >= hourArr[0] and time < hourArr[1]:
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
    
    if int(hour) == hourArr[0]:
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
    if timee == lunchTime:
        time.sleep(20*60)
        return True
    else:
        return False

def getPrevTime(hostname,database,username,pwd,port_id):
    #create connection to database
    conn = psycopg2.connect(
    host = hostname,
    dbname = database,
    user = username,
    password = pwd,
    port=port_id)
    cur = conn.cursor() #opens cursor (database stuff using psycopg2)
        
    execute="SELECT epoch_time FROM parts_timestamp WHERE ip_address='10.10.16.132' ORDER BY epoch_time DESC LIMIT 1;"

    cur.execute(execute) #executes the thing (idk I copied this from a tutorial and it works)
    result = cur.fetchone()
    #print("data fetched")
    cur.close()
    conn.close() #finished database updates
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


    cur.execute(insert_script, insert_values) #executes the thing (idk I copied this from a tutorial and it works)
    conn.commit()
    #print("Database updated")
    cur.close()
    conn.close() #finished database updates
    return timeEpoch

def findStation(sht,STATION):
    for i in range(5,64):
        if sht['C{}'.format(i)].value == STATION:
            return i
    

# MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ####



def main(filename,targetstat, endArr, breakArr, lunchArr,hourArr):
    # Setup
    

    #STARTS station     
    targetStation = station(targetstat)  # Station End of line OP100
    stationIP = targetStation.selectIP()

    #Initialization for database
    hostname = '10.110.19.205'
    database = 'timestamp'
    username = 'postgres'
    pwd = 'W1nter@2023Hydro' #Very safe, isn`t it lol
    port_id = 5432

    FIVE_MIN = 5*60
    SEC_HOURS = 3600
    print("Program running")
    
    
    while True:             # BEGINNING OF SHIFT ## BEGINNING OF SHIFT ## BEGINNING OF SHIFT ## BEGINNING OF SHIFT #

        resAfterAnHour = False
        happenedInFirst = False

        majorBucket=[]  # Resets all the overtime categories
        
        minorBucket=[]
        
        microBucket = []
        
        now = datetime.now()
        nowTime = now.strftime("%H")
        
        while inFirstHour(nowTime, hourArr) == False:   #waits for the next full shift to begin
            now = datetime.now()
            nowTime = now.strftime("%H")
        print("in shift")

        shift, endTime , breakPeriod, lunchTime  = whichShift(int(nowTime),endArr,breakArr,lunchArr,hourArr)  #finds out which shift it is
        happenedInFirst = firstHour(targetStation)
        if happenedInFirst == True:   # Tests for the first hour (anytime in the first hour counts as a full hour)
            shiftLength = (7.5 * SEC_HOURS)   # 8h - break times
            lastCycle = getPrevTime(hostname,database,username,pwd,port_id)
            databaseUpdate(stationIP,shift,lastCycle,hostname,database,username,pwd,port_id)

        else:
            resAfterAnHour,timeUsed = afterAnHour(endTime,targetStation)   #if not in first hour, checks for the next ones
            if resAfterAnHour == True:
                shiftLength = (6.5*SEC_HOURS) - timeUsed
                lastCycle = getPrevTime(hostname,database,username,pwd,port_id)
                databaseUpdate(stationIP,shift,lastCycle,hostname,database,username,pwd,port_id)
            else:
                shiftLength = 0 #DID NOT RUN

        # START/OPEN EXCEL FILE         
        timeNow = datetime.now()
        weekDay = timeNow.date().weekday() # 0 = Monday...
    
        if weekDay == 0 and shift == "day":
            wbChange = xw.Book(r"Master_table.xlsx")
            wbChange.save(r"workingTable\shifts_table.xlsx")
            wbChange.close()
         
        wb = xw.Book(r"workingTable\shifts_table.xlsx")
        

        if weekDay == 0:
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
        if shift == "afternoon":
            index+=1
        elif shift == "night":
            index+=2


        CYCLETIME = sht['F{}'.format(index)].value  # sec/part decided on the excel file 
        print(CYCLETIME)



        # MAIN PART OF SHIFT ## MAIN PART OF SHIFT ## MAIN PART OF SHIFT ## MAIN PART OF SHIFT ## MAIN PART OF SHIFT ## MAIN PART OF SHIFT #

        while now.strftime("%H:%M") != endTime:   #START CHECKING EVERY MOMENT
        
            pMde, timePerPart = checkPart(endTime,breakPeriod,lunchTime, targetStation) #calls function to check parts
            if pMde == False and timePerPart == 1:
                now = datetime.now()
                breakTime(now.strftime("%H:%M"),breakPeriod,lunchTime) 
                parts, timing = afterAnHour(endTime,targetStation)
                
            if pMde == True: #If a part is made, we check if it was over the cycletime and by how much
                lastCycle = getPrevTime(hostname,database,username,pwd,port_id)   # gets the last time a part was made for the calculations
                databaseUpdate(stationIP,shift,lastCycle,hostname,database,username,pwd,port_id) # saves the timestamp on a database
                if timePerPart > CYCLETIME:
                    if timePerPart - CYCLETIME > 3 *60: # over 3 min = Service
                        print("Major problem at: "+ str(now))
                        majorBucket.append(timePerPart-CYCLETIME)
                                        
                    else:                                   # Less than 3 min = micro
                        print("Micro problem at: "+ str(now))
                        microBucket.append(timePerPart-CYCLETIME)
                        

            now = datetime.now()
        print("END OF SHIFT")
        # END OF SHIFT HERE #### END OF SHIFT HERE #### END OF SHIFT HERE #### END OF SHIFT HERE #### END OF SHIFT HERE #### END OF SHIFT HERE ###
        
        nOfParts = targetStation.prodCounter()[0][3]
        time_awarded = nOfParts * CYCLETIME  #How much time was actually produced on this shift
        timeDiff = time_awarded - shiftLength
        
        nOfMajor = len(majorBucket)
        nOfMicro = len(microBucket)
        expectedNOfParts = int(shiftLength/CYCLETIME)

        
        timeMicro = 0
        timeMajor = 0

        

        for i in range(0, nOfMicro):    
            timeMicro = timeMicro + microBucket[i]   
        
        for i in range(0, nOfMajor):    
            timeMajor = timeMajor + majorBucket[i]

        # WRITING IN EXCEL ## WRITING IN EXCEL ## WRITING IN EXCEL ## WRITING IN EXCEL #
            
        

        sht['D{}'.format(index)].value = shiftLength/3600 # The original value was in seconds, so we transfer it into hours
        sht['E{}'.format(index)].value = time_awarded/3600
        sht['G{}'.format(index)].value = nOfParts
        sht['L{}'.format(index)].value = nOfMicro
        sht['N{}'.format(index)].value = nOfMajor
        sht['M{}'.format(index)].value = timeMicro/3600
        sht['O{}'.format(index)].value = timeMajor/3600




        wb.save(r"workingTable\shifts_table.xlsx")
        wb.close()


        #SENDING EMAIL##SENDING EMAIL##SENDING EMAIL##SENDING EMAIL##SENDING EMAIL##SENDING EMAIL##SENDING EMAIL##SENDING EMAIL##SENDING EMAIL#

        # create message object instance
        msg = MIMEMultipart()
        to_list = ["henrique.rodriques@martinrea.com"]  # ADD BRIAN AND SHUBHAM LATER
        # setup the parameters of the message
        password = "hiqrzmqfjltittct"   # VERY SECURE
        msg['From'] = "shiftreportshydroform@gmail.com"
        msg['To'] = ",".join(to_list)
        msg['Subject'] = "Shift Report"
        #msg['Cc'] = 'shubham.savani@martinrea.com'

        # add in the message body
        msg.attach(MIMEText("Here is the shift report for: "+ shift +' of ' + datetime.today().strftime('%Y-%m-%d') + " :"))

        # attach a file
        with open("workingTable\shifts_table.xlsx", "rb") as f:
            attach = MIMEApplication(f.read(),_subtype="txt")
            attach.add_header('Content-Disposition','attachment',filename=str("table_shifts.xlsx"))
            msg.attach(attach)

        # create server
        server = smtplib.SMTP('smtp.gmail.com', 587)

        # start TLS for security
        server.starttls()

        # Login
        server.login(msg['From'], password)

        # send the message via the server.
        server.sendmail(msg['From'], to_list, msg.as_string())

        # terminate the SMTP session
        server.quit()
