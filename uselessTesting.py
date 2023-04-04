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

# wb = xw.Book(r"Master_table.xlsx")
# sht = wb.sheets['Mon']
# def findStartion(sht,STATION):
#     for i in range(5,64):
#         if sht['C{}'.format(i)].value == STATION:
#             return i
    
#NOW WE NEED TO FIND OUT WHAT DAY OF THE WEEK IT IS AND WRITE INFO ON APPROPRIATE SPOT.
timeNow = datetime.now()
print(timeNow.date().weekday())  # 0 = Monday...


# wb.save("master_table_testing.xlsx")
# wb.close()

