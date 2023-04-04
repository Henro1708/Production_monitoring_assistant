from main import main
from multiprocessing import Process

if __name__ == "__main__":
        
    xlfilename = ['table_shiftsJLLong.xlsx']
    stations = ["JLLONG"]

    procs = []

    for i in range(len(xlfilename)):
        proc = Process(target = main, args = (xlfilename[i],stations[i],))
        procs.append(proc)
        proc.start()
    for proc in procs:
        proc.join()

    


