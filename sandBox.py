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

targetStation = station("JLLONG")
targetStationIpAdd = targetStation.selectIP()


def firstHour(targetStation):               # Checks if a part is made on the first hour 

        
    t1 = time.time()
    t2 = time.time()
    while (t1 - t2) < 3600:   #seconds in an hour
        if (targetStation.onePart()[0][3]) == 1:          #PLC says a part is made  
            print("First part made! (First hour): {}".format(targetStation))
            return True
        t1=time.time()
    return False

    
firstHour(targetStation)