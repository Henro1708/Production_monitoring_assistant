
import plc
from plc import station
import time


# Initialising station  


JLLong = station("P1")
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


    #print("START MONITORING - JLLong")
    
    #print(bool(JLLong.onePart()[0][3]))
        
    print(JLLong.prodCounter()[0][3])
    #print(JLLong.prodHourCounter())
    #time.sleep(1)
    #print ("##################")
    