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

shift="testing"

msg = MIMEMultipart()
to_list = ["henriqueengelke@gmail.com", "henrique.rodriques@martinrea.com"]
    # setup the parameters of the message
password = "hiqrzmqfjltittct"   # VERY SECURE
msg['From'] = "shiftreportshydroform@gmail.com"
msg['To'] =  ",".join(to_list)
msg['Subject'] = "Shift Report"
msg['Cc'] = 'henriqueengelke@gmail.com'

msg.attach(MIMEText("Here is the shift report for: "+ shift +' of ' + datetime.today().strftime('%Y-%m-%d') + " :"))

server = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
server.starttls()

    # Login
server.login(msg['From'], password)

    # send the message via the server.
server.sendmail(msg['From'], to_list, msg.as_string())

    # terminate the SMTP session
server.quit()

