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




def testingTimes():
    print("TESTING STARTED")
    JLLongCD = station("CD4FR")
    JLLongIpAddCD = JLLongCD.selectIP()
    JLLong = station("JLLONG")
    JLLongIpAddJL = JLLong.selectIP()
    JLLongEL = station("ELCV")
    JLLongIpAddEL = JLLongEL.selectIP()
    valueCD = 0
    valueJL=0
    valueEL=0
    while True:
        oldJL = valueJL
        oldEL = valueEL
        oldCD = valueCD
        valueCD = JLLongCD.prodCounter()[0][3]
        valueJL = JLLong.prodCounter()[0][3]
        valueEL = JLLongEL.prodCounter()[0][3]
        if oldCD > valueCD:
            timeNow = datetime.now()
            print("Counter reset at CD4 at {}".format(timeNow.strftime("%H:%M")))

        if oldEL > valueEL:
            timeNow = datetime.now()
            print("Counter reset at ELCV at {}".format(timeNow.strftime("%H:%M")))

        if oldJL > valueJL:
            timeNow = datetime.now()
            print("Counter reset at JLLong at {}".format(timeNow.strftime("%H:%M")))
        time.sleep(5)


testingTimes()