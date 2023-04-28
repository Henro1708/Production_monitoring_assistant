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

def addNum(num):
    res = 0
    numStr = str(num)
    for i in numStr:
        res += int(i)
    
    return res

num = 245

    
numStr = str(num)

print(len(numStr))
    # num2 = addNum(num)
    # numStr = str(num2)


