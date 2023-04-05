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
targetstat = "JLLONG"
shift = "day"
# wb = xw.Book(r"Master_table.xlsx")
# sht = wb.sheets['Mon']
def findStation(sht,STATION):
    for i in range(5,64):
        if sht['C{}'.format(i)].value == STATION:
            return i
    
#NOW WE NEED TO FIND OUT WHAT DAY OF THE WEEK IT IS AND WRITE INFO ON APPROPRIATE SPOT.




timeNow = datetime.now()
weekDay = timeNow.date().weekday() # 0 = Monday...
weekDay = 0
if weekDay == 0 and shift == "day":
    wbChange = xw.Book(r"Master_table.xlsx")
    wbChange.save(r"workingTable\shifts_table.xlsx")
    wbChange.close()
    
wb = xw.Book(r"workingTable\shifts_table.xlsx")
if shift == "night":
    if weekDay == 0:
        
        weekDay = 6
    else:
        weekDay -=1

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

sht['D{}'.format(index)].value = round(shiftLength/3600,3) # The original value was in seconds, so we transfer it into hours
sht['E{}'.format(index)].value = round(time_awarded/3600,3)
sht['G{}'.format(index)].value = nOfParts
sht['L{}'.format(index)].value = nOfMicro
sht['N{}'.format(index)].value = nOfMajor
sht['M{}'.format(index)].value = round((timeMicro/3600),3)
sht['O{}'.format(index)].value = round((timeMajor/3600),3)




wb.save(r"workingTable\shifts_table.xlsx")
wb.close()

