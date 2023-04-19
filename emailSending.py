import time
from datetime import datetime
from pylogix import PLC
from plc import station
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import xlwings as xw

def sendEmail():
    print("Email started up")
    while True:
        timeNow = datetime.now()
        while timeNow.strftime("%H:%M") != '00:01' and timeNow.strftime("%H:%M") != '15:05' and timeNow.strftime("%H:%M") != '07:05':
            timeNow = datetime.now()
        
        now = datetime.now()
        day = now.strftime("%D")
        

        # create message object instance
        msg = MIMEMultipart()
        to_list = ["henrique.rodriques@martinrea.com", "henriqueengelke@gmail.com"]  # ADD BRIAN AND SHUBHAM LATER
        # setup the parameters of the message
        password = "hiqrzmqfjltittct"   # VERY SECURE
        msg['From'] = "shiftreportshydroform@gmail.com"
        msg['To'] = ",".join(to_list)
        msg['Subject'] = "Shift Report for {}".format(day)
        #msg['Cc'] = 'shubham.savani@martinrea.com'

        # add in the message body



        msg.attach(MIMEText("Here is the most updated shift report as of {} :".format(day)))
        #print(day)

        # attach a file
        with open("workingTable\shifts_table.xlsx", "rb") as f:
            attach = MIMEApplication(f.read(),_subtype="txt")
            attach.add_header('Content-Disposition','attachment',filename=str("Shifts_report.xlsx"))
            msg.attach(attach)

        # create server
        server = smtplib.SMTP('smtp.gmail.com', 587)

        # start TLS for security
        server.starttls()

        # Login
        server.login(msg['From'], password)

        # send the message via the server.
        server.sendmail(msg['From'], to_list, msg.as_string())

        # terminate the session
        server.quit()

        now = datetime.now()
        weekDay = now.date().weekday()
        if timeNow.strftime("%H") == "15" and weekDay == 0:
            wbChange = xw.Book(r"Master_table.xlsx") #opens the original and saves a copy on the working folder
            wbChange.save(r"workingTable\shifts_table.xlsx")
            wbChange.close()
        time.sleep(65)