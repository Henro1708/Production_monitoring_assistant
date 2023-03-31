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



#Initialization for database
hostname = '10.110.19.205'
database = 'timestamp'
username = 'postgres'
pwd = 'W1nter@2023Hydro' #Very safe, isn`t it lol
port_id = 5432

def databaseUpdate(IP,shift,prevTime):
   #create connection to database
    conn = psycopg2.connect(
    host = hostname,
    dbname = database,
    user = username,
    password = pwd,
    port=port_id)

    timeEpoch = time.time()
    cur = conn.cursor() #opens cursor (database stuff using psycopg2)

                #SQL code \/
    insert_script = 'INSERT INTO parts_timestamp(ip_address, epoch_time, time_diff ,shift) VALUES(%s, %s, %s,%s)'
    insert_values = (IP, timeEpoch, timeEpoch-prevTime ,shift)


    cur.execute(insert_script, insert_values) #executes the thing (idk I copied this from a tutorial and it works)
    conn.commit()
    #print("Database updated")
    cur.close()
    conn.close() #finished database updates
    return timeEpoch

def getPrevTime():
    #create connection to database
    conn = psycopg2.connect(
    host = hostname,
    dbname = database,
    user = username,
    password = pwd,
    port=port_id)
    cur = conn.cursor() #opens cursor (database stuff using psycopg2)
        
    execute="SELECT epoch_time FROM parts_timestamp WHERE ip_address='10.10.16.132' ORDER BY epoch_time DESC LIMIT 1;"

    cur.execute(execute) #executes the thing (idk I copied this from a tutorial and it works)
    result = cur.fetchone()
    #print("data fetched")
    cur.close()
    conn.close() #finished database updates
    if result == None:
        return time.time()
    else:
        return result[0]
IP = '10.10.16.132'
databaseUpdate(IP, 'test', 0)
