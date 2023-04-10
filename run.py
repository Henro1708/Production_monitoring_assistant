from main import main
from multiprocessing import Process
from emailSending import sendEmail

if __name__ == "__main__": #this is necessary to make sure the thing exists
        
    stations = ["JLLONG", "CD4FR","P1"]

    procs = [] #array for all the processes that will be started

    #Times
    lunchJLLong = ["12:30", "20:30", "04:45"]    # Missing lunch and break times for other stations
    breakJLLong = ["09:30","17:30","01:45"]      # P1 part made signal is inconcistent
    endTimeJLLong = ["14:59", "22:59", "06:59"]    # ELCV signal is opposite to what it should be
    firstHoursJLLong = [7, 15, 23]

    lunchArrays =[lunchJLLong, "Test"]
    breakArrays = [breakJLLong, 'Test']
    endTimeArrays = [endTimeJLLong, 'Test']
    firstHourArrays = [firstHoursJLLong, 'Test']

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


    


