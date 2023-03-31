import time
from datetime import datetime

a = '08:19'
def timee(ti):

    if ti == a:
        time.sleep(10*1)
        return True
    else: 
        return False
timeNow = datetime.now()
print(timee(timeNow.strftime("%H:%M")))