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
import os

# THIS PROGRAM IS ALMOST EQUAL TO main.py, EXCEPT THE TRIGGER FOR the PARTS MADE IS BASED ON THE COUNT


#Checking start time and assigning an appropriate shitft length

def firstHour(targetStation):              # Checks if a part is made on the first hour 
    
    try:
        t1 = time.time()
        t2 = time.time()
        value = targetStation.prodCounter()[0][3]
        previousValue = value
        while (t1 - t2) < 360:   #seconds in an hour
            value = targetStation.prodCounter()[0][3]
            if value == None:
                value = 0
            if previousValue == None:
                previousValue = 0
            if value > previousValue:          #PLC tells us the counter and it sees if it has changed. Needs to be done because Part done signal is too quick  
                print("First part made! (First hour): {}".format(targetStation))
                return True,t1-t2
            t1=time.time()
        return False,0
    except:
        print("socket fail {}".format(targetStation))
        return False,0


def afterAnHour(endTime, targetStation): # checks the time a part takes to be made after the first hour
    try:
        t1 = time.time()
        t2 = time.time()

        value = targetStation.prodCounter()[0][3]
        previousValue = value
        if value == None:
            value = 0
        if previousValue == None:
            previousValue = 0
        while value <= previousValue: #PLC tells when part is made
            value = targetStation.prodCounter()[0][3]
            if value == None:
                value = 0
            if previousValue == None:
                previousValue = 0
            timeNow = datetime.now()
            if timeNow.strftime("%H:%M") == endTime:   # If it is not the end of the shift, keep checking until a part is made
                return False,0
            t2 = time.time()
        print("Part made! (Not first hour)")
        return True, (t2-t1)
    except:
        print("socket fail {}".format(targetStation))
        return False,-1

def checkTime(targetStation,endTime):
    try:
        t2 = time.time()
        t1 = time.time()
        
        value = targetStation.prodCounter()[0][3]
        previousValue = value

        if value == None:
            value = 0
        if previousValue == None:
            previousValue = 0

        while value <= previousValue: #PLC tells when part is made
            value = targetStation.prodCounter()[0][3]

            if value == None:
                value = 0
            if previousValue == None:
                previousValue = 0


            timeNow = datetime.now()
            if timeNow.strftime("%H:%M") == endTime:   # If it is not the end of the shift, keep checking until a part is made
                return False,-1
            if t2-t1 >120:
                return False,0
            t2 = time.time()
        #print("Part was made at Presses")
        return True , t2-t1
    except:
        print("socket fail {}".format(targetStation))
        return False,-2


def whichShift(time, endArr,hourArr):       # Tells which shift we are in and when it will end
    
    if time >= hourArr[0] and time < hourArr[1]:   # These values are passed as parameters from the other file (run.py)
        print("day shift")
        return "day" , endArr[0] 
    elif time >= hourArr[1] and time < hourArr[2]:
        print("afternoon shift")
        return "afternoon", endArr[1]
    elif time  >= hourArr[2] or time < hourArr[0]:
        print("night shift")
        return "night" , endArr[2]
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
        return True #CHANGE    




def findStation(sht,STATION):  # Loops through the excel file and finds which row has the expected station
    for i in range(5,64):
        if sht['C{}'.format(i)].value == STATION:
            return i #returns the row


def excelWrite(shift, targetstat, shiftLength):
    with xw.App() as app:
        timeNow = datetime.now()
        weekDay = timeNow.date().weekday() # 0 = Monday...
        if shift == "night":
            if weekDay == 0:
                weekDay =6
            else:
                weekDay -=1



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
        index = findStation(sht,targetstat) # finds the row we will be edditing based on the station we are monitoring
        if shift == "afternoon":
            index+=1
        elif shift == "night":
            index+=2

        sht['D{}'.format(index)].value = shiftLength/3600 # The original value was in seconds, so we transfer it into hours

        wb.save(r"workingTable/shifts_table.xlsx")
        wb.close()
        

# MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ##### MAIN ####


def mainAlt(targetstat, endArr,hourArr): #parameters are station, end times for all shifts as an array, break times, lunchtimes, and shift start times (arrays)
    # Setup
    

    #STARTS station     
    targetStation = station(targetstat)  # Station End of line OP100
    stationIP = targetStation.selectIP()

    

    SEC_HOURS = 3600
    print("Program with alternative count running: " + targetstat)

    while True:             # BEGINNING OF SHIFT ## BEGINNING OF SHIFT ## BEGINNING OF SHIFT ## BEGINNING OF SHIFT #

        resAfterAnHour = False
        happenedInFirst = False

        
        now = datetime.now()
        nowTime = now.strftime("%H")
        
        while inFirstHour(nowTime, hourArr) == False:   #this waits for the next full shift to start
            now = datetime.now()
            nowTime = now.strftime("%H")
        #print("in shift")

        shift, endTime = whichShift(int(nowTime),endArr,hourArr)  #finds out which shift it is
        
        happenedInFirst,timeFirst = firstHour(targetStation) #returns a bool that indicates whether production was started in the first hour of the shift or not
        if happenedInFirst == True:   # Tests for the first hour (anytime in the first hour counts as a full shift worked)
            shiftLength = (7.5 * SEC_HOURS)   # 8h - break times
            
        else:
            try:
                resAfterAnHour,timeUsed = afterAnHour(endTime,targetStation)   #if production was not strarted in the first hour, it checks when a part is made or iof the shift is over
                if resAfterAnHour == True: #if a part was made
                    shiftLength = (6.5*SEC_HOURS) - timeUsed #this determines the amount of time worked on the shift
                    
                else:
                    shiftLength = 0 #DID NOT RUN
            except:
                resAfterAnHour,timeUsed = afterAnHour(endTime,targetStation)   #if production was not strarted in the first hour, it checks when a part is made or iof the shift is over
                if resAfterAnHour == True: #if a part was made
                    shiftLength = (6.5*SEC_HOURS) - timeUsed #this determines the amount of time worked on the shift
                    
                else:
                    shiftLength = 0 #DID NOT RUN 
      
        
        
        # MAIN PART OF SHIFT ## MAIN PART OF SHIFT ## MAIN PART OF SHIFT ## MAIN PART OF SHIFT ## MAIN PART OF SHIFT ## MAIN PART OF SHIFT #
        
        
        while now.strftime("%H:%M") != endTime:   #START CHECKING EVERY MOMENT
            now = datetime.now()
            
        

                
        print("END OF SHIFT")
        # END OF SHIFT HERE #### END OF SHIFT HERE #### END OF SHIFT HERE #### END OF SHIFT HERE #### END OF SHIFT HERE #### END OF SHIFT HERE ###
        
        
        
        
        # WRITING IN EXCEL ## WRITING IN EXCEL ## WRITING IN EXCEL ## WRITING IN EXCEL #
        
        excelWrite(shift, targetstat, shiftLength)
        
        

