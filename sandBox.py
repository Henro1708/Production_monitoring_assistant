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

targetStation = station("P1")
targetStationIpAdd = targetStation.selectIP()
endTime = "09:10"

def checkTime(targetStation,endTime):
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
    print("Part was made at Presses")
    return True , t2-t1


t2 = time.time()
t1 = time.time()
timeArray = []
now = datetime.now()
while now.strftime("%H:%M") != endTime:   #START CHECKING EVERY MOMENT

    pMdeRes, timeTaken = checkTime(targetStation,endTime)
    if pMdeRes == True:
        timeArray.append(timeTaken)
    else:
        pass
    now = datetime.now()




shiftLength = 0
for i in timeArray:
    shiftLength+=i
print(shiftLength)