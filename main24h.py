import time
from datetime import datetime
from plc import station
import psycopg2
from datetime import date







stationn= "OP090"     #STATION
nOfRobots = 2
nOfLC = 2

minToInactivity = 1 #Time used in the functions
minToInactivity3 = 0.5
timeToInactivity3 = minToInactivity3 *60
timePerCycle = 6 #time for each cycle
nOfCycles = 240  # the number of cycles of 6 min in a day

timePCSec = timePerCycle *60 
timeToInactivity =minToInactivity *60 
minToInactivity2 = 2    # time used to test for laser curtain and button swipe
timeToInactivity2 =minToInactivity2 *60 



# FUNCTIONS   ################################################
def writeFile(message):  # Used to writte any message on the hours.txt file
    file = open( 'hours.txt', 'a')
    file.write(message+"\n")
    file.close()
    


def laserCurtain():
    #print("laser curtain checking")#TEST
    t1 = time.time()   #starts time
    t0 = time.time()

    if nOfLC == 2:    #expects to know how many laser curtains there are on the station and checks for 2                                           
        while (t1-t0) < timeToInactivity2: 
            
            if OP090.lcTag()[0][3] ==1 or OP090.lcTag()[1][3] == 1: #receives from PLC (first index is number of station, second is the information we want)
                return True, (t1-t0)
            t1=time.time()
            
        return False, timeToInactivity2
    
    elif nOfLC == 1:   # if there are only one, it checks for one
        while (t1-t0) < timeToInactivity2: 
            
            if OP090.lcTag()[0][3] ==1: #receives from PLC (first index is number of station, second is the information we want)
                return True, (t1-t0)  #returns how much time was used, so we can know how much time to wait later
            t1=time.time()
        return False, timeToInactivity2
    

def buttonSwipe():      # Tests if the button is swipped in 2 minutes (Follows the same structure as the LC one, but there is always just one button)                                   
    
   
    t3 = time.time()
    t2 = time.time()
    
        
    while (t3-t2) < timeToInactivity2:
        if OP090.swipeButton()[0][3] ==1: 
            return True, (t3-t2)
        t3=time.time()
        #print(t3-t2) #TEST
    return False, timeToInactivity2

def gates():      # Tests if the gates are oppened in 30s (Same structure as the LC one)                                   
    

    t4 = time.time()
    t5 = time.time()

    while (t4-t5) < timeToInactivity3:
        if OP090.safetyGate()[0][3] == 0:   #gates open = 0
            return True, (t4-t5) 
        t4=time.time()
        #print(t4-t5) #TEST
    return False, timeToInactivity3
        
    
    

def robotWorking():
    #print("test robot working") #TEST
    t1 = time.time()
    t0 = time.time()
    if nOfRobots == 4:
        
        while (t1-t0) < timeToInactivity: 
            if OP090.robotRunning()[0][3] ==1 or OP090.robotRunning()[1][3] ==1 or OP090.robotRunning()[2][3] ==1 or OP090.robotRunning()[3][3] ==1: #PLC tells if the robot is working
                remainingTime = t1-t0
                #print("Robot ON.")
                
                return True, remainingTime
            t1=time.time()
            #print(t1-t0) #TEST
        return False, timeToInactivity
    elif nOfRobots == 3:

        while (t1-t0) < timeToInactivity: 
            if OP090.robotRunning()[0][3] ==1 or OP090.robotRunning()[1][3] ==1 or OP090.robotRunning()[2][3] ==1: #PLC tells if the robot is working
                remainingTime = t1-t0
                #print("Robot ON.")
                
                return True, remainingTime
            t1=time.time()
            #print(t1-t0) #TEST
        return False, timeToInactivity
    elif nOfRobots == 2:  

        while (t1-t0) < timeToInactivity: 
            if OP090.robotRunning()[0][3] ==1 or OP090.robotRunning()[1][3] ==1: #PLC tells if the robot is working
                remainingTime = t1-t0
                #print("Robot ON.")
                
                return True, remainingTime
            t1=time.time()
            #print(t1-t0) #TEST
        return False, timeToInactivity
    elif nOfRobots == 1:

        while (t1-t0) < timeToInactivity: 
            if OP090.robotRunning()[0][3] ==1: #PLC tells if the robot is working
                remainingTime = t1-t0
                #print("Robot ON.")
                
                return True, remainingTime
            t1=time.time()
            #print(t1-t0) #TEST
        return False, timeToInactivity

def fullAuto():  # Tests if the robots are in auto mode (not being controlled manually)

    print("test if full auto") # TEST
    if OP090.robotAuto()[0][3] ==1: #PLC tells if the line is on auto
        return True
    return False

#MAIN ###########################################################################################################################################

#initialization of station
OP090 = station(stationn)
ipAdd = OP090.selectIP()

#Initialization for database
hostname = 'localhost'
database = 'scheduler_times'
username = 'postgres'
pwd = 'W1nter@2023Hydro' #Very safe, isn`t it lol
port_id = 5432


#variables
lastStatus = 0
secondLastStatus = 0
status = 0 

#main loop
while True:    # after starting the program, it should never end

    #create connection to database
    conn = psycopg2.connect(
    host = hostname,
    dbname = database,
    user = username,
    password = pwd,
    port=port_id)
    
    # calls the functions and analizes them
    dayResult = []
    for i in range(nOfCycles): #times cycle will run in a day (240 now) #IT IS JUST FOR 12 MIN NOW
        print("Cycle "+ str(i+1)+ "/" + str(nOfCycles))
        secondLastStatus = lastStatus
        lastStatus = status
        lcRes, lcTime = laserCurtain()
        btnRes, btnTime = buttonSwipe()
        gateRes, gateTime = gates()
        robotRes,robotTime = robotWorking()
        autoRes = fullAuto()
        print("ALL FUNCTIONS FINISHED") #TESTTT
        if (robotRes == 1 and gateRes == 0 and btnRes == 1 and lcRes == 1):
            status = 1 #Operating
        elif (lcRes == 1 and btnRes == 0 and lastStatus == 3 and secondLastStatus == 3) or (gateRes == 1 and lastStatus == 3 and secondLastStatus == 3):
            status = 2 # first maintenance
        elif (lcRes == 1 and btnRes == 0 and (lastStatus == 2 or lastStatus == 4)) or (gateRes == 1 and (lastStatus == 2 or lastStatus == 4)) or (autoRes == 0):
            status = 4 #maintenance
        elif (lcRes == True and btnRes == False and robotRes == False and secondLastStatus != 3 and (secondLastStatus !=0 and lastStatus !=0)) or (gateRes == True and secondLastStatus != 3 and (secondLastStatus !=0 and lastStatus !=0)):
            status = 3 #Operation maintenacne (quick fix)
        elif robotRes == 0 and btnRes == 0 and lcRes==0:
            status = 0 #not scheduled
        elif (lcRes == 1 and btnRes == 0 and robotRes == 0 and (lastStatus == 0 or secondLastStatus == 0)) or (gateRes == 1 and (lastStatus == 0 or secondLastStatus == 0)) or (autoRes == 0 and (lastStatus == 0 or secondLastStatus == 0) ):
            status = 6 #Maintenance out of hours (not a problem and is considered down time)
        else:
            print("values confusing. happened at cycle: ", i+1)
            print("results were: lc:", lcRes, "swipe:", btnRes, "Auto:", autoRes, "last Status:", lastStatus,"second last:", secondLastStatus, "Robot result:", robotRes, "gates:", gateRes)
            status = 7 #confused and does not fit any of the options above 
        
        dayResult.append(status) #saves the result into an array that will be read later
        
        time.sleep((timePCSec)-(lcTime+btnTime+gateTime+robotTime)) # waits until the 6 minutes cycle finish 
    #For loop ends here, the next section only happens each 24h

    tInMaintenance = 0
    tInOperation = 0
    tDown = 0
    tInQuickFix = 0
    tConfused = 0
    
    for index,result in enumerate(dayResult, start = 0): # reads the array and counts the time for each case
        if result == 0: #down time
            tDown +=timePerCycle
        if result == 1: #operating
            tInOperation +=timePerCycle
        if result == 2:   # first maintenance had 2 quick fix checks before, so we correct those and we add that time to full maintenance
            tInMaintenance +=(3*timePerCycle)
            tInQuickFix -=(2*timePerCycle)
        if result==3:   #just a quick fix done by the operators
            tInQuickFix +=timePerCycle
        if result==4:  #maintenance (only counts after 12 min of stopped time)
            tInMaintenance +=timePerCycle
        if result ==6:  #out of schedule maintenance (counts as down time)
            tDown +=timePerCycle
        if result == 7:   #here we check why this happened and why it was confused
            print("values confusing. happened at cycle: ", index+1)
            tConfused +=timePerCycle
        

    day = date.today() # writes on the file all the times
    writeFile("END OF TESTING. Results for " + str(day)  +" On station: "+ stationn+ ": \n")
    writeFile("Time in Operation: " + str(tInOperation) + " min ")
    writeFile("Not Scheduled time: "+ str(tDown) + " min")
    writeFile("Time for quick fixes: "+ str(tInQuickFix) + " min ")
    writeFile("Time in Maintnance: "+ str(tInMaintenance)+ " min ")
    writeFile("Time in confusion: "+ str(tConfused)+ " min \n")
    print("file updated")

    cur = conn.cursor() #opens cursor (database stuff using psycopg2)

                #SQL code \/
    insert_script = 'INSERT INTO bt1xx(date, operatingTime, quickfixtime, maintenancetime ,downtime, confusedtime) VALUES(current_timestamp, %s,%s,%s,%s,%s)'
    insert_values = (tInOperation, tInQuickFix, tInMaintenance,tDown, tConfused)


    cur.execute(insert_script, insert_values) #executes the thing (idk I copied this from a tutorial and it works)
    conn.commit()
    print("Database updated")
    cur.close()
    conn.close() #finished database updates

    #end of while True loop (everything will start over now from the beginning)