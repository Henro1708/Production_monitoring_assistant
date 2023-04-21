from main import main
from multiprocessing import Process
from emailSending import sendEmail
from alternativeCount import mainAlt


if __name__ == "__main__": #this is necessary to make sure the thing exists
        
    stationsMain = ["JLLONG", "CD4FR","ELCV"]

    alternativeStations = ["P1", "P3"]

    procs = [] #array for all the processes that will be started
    procsA = [] #array for all the processes that will be started

    #Times
    # TIMES CD4FR
    lunchCD4 = ["12:00", "20:00", "04:15"]   # No night shift, so that time is not important
    breakCD4 = ["08:30","17:00","01:15"] 
    endTimeCD4 = ["13:59", "21:59", "05:59"]  #Make end times different so they don`t interfere with one another`    
    firstHoursCD4 = [6, 14, 22]
    # TIMES ELCV
    lunchELCV = ["12:30", "20:00", "04:15"] 
    breakELCV = ["08:30","17:00","01:15"]   # NO night shifts, so the timing there is not important
    endTimeELCV = ["14:57", "22:57", "06:57"]    
    firstHoursELCV = [7, 15, 23]

    # TIMES FOR JLLONG
    lunchJLLong = ["12:30", "20:30", "04:45"]    # Array for all lunch break times, lunch break at day shift, afternoon and night
    breakJLLong = ["09:30","17:30","01:45"]      # Same for regular breaks
    endTimeJLLong = ["14:59", "22:59", "06:59"]    # Times the shifts end      
    firstHoursJLLong = [7, 15, 23]

    # TIME PRESSES // They use alternative monitoring because their part made signal is unoticable most of the time
    
    endTimeP = ["13:57", "21:57", "05:57"]  
    firstHoursP = [6, 14, 22]


    lunchArrays =[lunchJLLong, lunchCD4,lunchELCV]
    breakArrays = [breakJLLong, breakCD4,breakELCV ]
    endTimeArrays = [endTimeJLLong, endTimeCD4,endTimeELCV ]
    firstHourArrays = [firstHoursJLLong, firstHoursCD4, firstHoursELCV]

    # ALternative arrays  # Arrays for alternative monitoring process
    
    endTimeArraysAlt = [endTimeP,endTimeP]
    firstHourArraysAlt = [firstHoursP,firstHoursP]

    
    #starting the processes

    email = Process(target = sendEmail)
    email.start()
    for i in range(len(stationsMain)):
        proc = Process(target = main, args = (stationsMain[i],endTimeArrays[i],breakArrays[i] ,lunchArrays[i],firstHourArrays[i], ))
        
        procs.append(proc)
        proc.start() #Starts proccesses
    
    for i in range(len(alternativeStations)):
        procA = Process(target = mainAlt, args = (alternativeStations[i],endTimeArraysAlt[i],firstHourArraysAlt[i], ))
    
        procsA.append(procA)
        procA.start() #Starts proccesses
    
    for procA in procsA:
        procA.join() #this ensures the processes end together (not critiacal here)

    for proc in procs:
        proc.join() #this ensures the processes end together (not critiacal here)


    email.join()


    


