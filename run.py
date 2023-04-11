from main import main
from multiprocessing import Process
from emailSending import sendEmail

if __name__ == "__main__": #this is necessary to make sure the thing exists
        
    stations = ["JLLONG", "CD4FR","ELCV"]

    procs = [] #array for all the processes that will be started

    #Times
    # TIMES CD4FR
    lunchCD4 = ["12:00", "20:00", "04:15"]   # No night shift, so that time is not important
    breakCD4 = ["08:30","17:00","01:15"] 
    endTimeCD4 = ["14:59", "22:59", "06:59"] 
    firstHoursCD4 = [7, 15, 23]
    # TIMES ELCV
    lunchELCV = ["12:30", "20:00", "04:15"] 
    breakELCV = ["08:30","17:00","01:15"]   # NO night shifts, so the timing there is not important
    endTimeELCV = ["14:59", "22:59", "06:59"] 
    firstHoursELCV = [7, 15, 23]

    # TIMES FOR JLLONG
    lunchJLLong = ["12:30", "20:30", "04:45"]    # Missing lunch and break times for other stations
    breakJLLong = ["09:30","17:30","01:45"]      
    endTimeJLLong = ["14:59", "22:59", "06:59"]    
    firstHoursJLLong = [7, 15, 23]

    lunchArrays =[lunchJLLong, lunchCD4,lunchELCV]
    breakArrays = [breakJLLong, breakCD4,breakELCV ]
    endTimeArrays = [endTimeJLLong, endTimeCD4,endTimeELCV ]
    firstHourArrays = [firstHoursJLLong, firstHoursCD4, firstHoursELCV]

    #starting the processes
    email = Process(target = sendEmail)
    email.start()
    for i in range(len(stations)):
        proc = Process(target = main, args = (stations[i],endTimeArrays[i],breakArrays[i] ,lunchArrays[i],firstHourArrays[i], ))
        
        procs.append(proc)
        proc.start() #Starts proccesses
    for proc in procs:
        proc.join() #this ensures the processes end together (not critiacal here)

    email.join()

#830 12pm 5pm 8pm
    


