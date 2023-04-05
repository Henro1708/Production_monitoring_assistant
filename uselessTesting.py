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


lunchJLLong = ["12:30", "20:30", "04:45"]
breakJLLong = ["09:30","17:30","01:45"]
endTimeJLLong = ["14:59", "22:59", "06:59"]

firstHoursJLLong = [7, 15, 23]
lunchJLLong = ["12:30", "20:30", "04:45"]
breakJLLong = ["09:30","17:30","01:45"]
endTimeJLLong = ["14:59", "22:59", "06:59"]
firstHoursJLLong = [7, 15, 23]

lunchArrays =[lunchJLLong, "Test"]
breakArrays = [breakJLLong, 'Test']
endTimeArrays = [endTimeJLLong, 'Test']
firstHourArrays = [firstHoursJLLong, 'Test']




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
