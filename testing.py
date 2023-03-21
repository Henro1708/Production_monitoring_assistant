
import plc
from plc import station
import time


# Initialising station  

OP090 = station("OP090")
ipAdd = OP090.selectIP()

FR120 = station("FR120")
FR120ipAdd = FR120.selectIP()

OP100 = station("OP100")
OP100ipAdd = OP100.selectIP()

OP120 = station("OP120")
OP120ipAdd = OP120.selectIP()

JLLong = station("JLLONG")
JLLongIpAdd = JLLong.selectIP()


#########################################

"""
output for each tag contains following elements
Element 1: Staion name which is being called
Element 2: Name of Tag
Element 3: Instance number (If more than one i.e. Robot, Safety Door)
Element 4: Value of Tag
"""

######################################
while True:


    print("START MONITORING - JLLong")

    
    print(JLLong.onePart()[0][3])
    print(JLLong.prodCounter()[0][3])
    #print(JLLong.prodHourCounter())

    print ("##################")
    time.sleep(5)