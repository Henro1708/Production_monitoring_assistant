from main import main
from multiprocessing import Process

if __name__ == "__main__":
        
    xlfilename = ['table_shiftsJLLong.xlsx', 'test.xlsx']
    stations = ["JLLONG", "TEST"]

    procs = []

    lunchJLLong = ["12:30", "20:30", "04:45"]
    breakJLLong = ["09:30","17:30","01:45"]
    endTimeJLLong = ["14:59", "22:59", "06:59"]
    firstHoursJLLong = [7, 15, 23]

    lunchArrays =[lunchJLLong, "Test"]
    breakArrays = [breakJLLong, 'Test']
    endTimeArrays = [endTimeJLLong, 'Test']
    firstHourArrays = [firstHoursJLLong, 'Test']


    for i in range(len(xlfilename)):
        proc = Process(target = main, args = (xlfilename[i],stations[i],endTimeArrays[i],breakArrays[i] ,lunchArrays[i],firstHourArrays[i] ))
        procs.append(proc)
        proc.start()
    for proc in procs:
        proc.join()

    


