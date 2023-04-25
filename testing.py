
import plc
from plc import station
import time
from datetime import datetime
import pandas as pd
import xlwings as xw

def findStation(sht,STATION):  # Loops through the excel file and finds which row has the expected station
    for i in range(5,64):
        if sht['C{}'.format(i)].value == STATION:
            return i #returns the row


def excelWrite(shift, targetstat, shiftLength, time_awarded, nOfParts, nOfMicro, nOfMajor, timeMicro, timeMajor):
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
        sht['E{}'.format(index)].value = time_awarded/3600
        sht['H{}'.format(index)].value = nOfParts
        sht['L{}'.format(index)].value = nOfMicro
        sht['O{}'.format(index)].value = nOfMajor
        sht['N{}'.format(index)].value = timeMicro/3600
        sht['Q{}'.format(index)].value = timeMajor/3600

        wb.save(r"workingTable\shifts_table.xlsx")
        wb.close()


excelWrite("night", "P1",12*3600,36000, 255, 1, 2, 357, 688)