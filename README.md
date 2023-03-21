This repository serves the purpose of storing the files from the scheduler.

Here is an explanation of each file: 
    checkParts.py:
    - checks when a part is made on JL Long line and saves it into a postgres database (all info for it is on the code)
    - Later this will be able to connect the database with excel and make some good graphs showing how well parts are being made
    
    shifts2.0.py:
    -At the end of every shift, it updates an excel file with the time spent in error etc on station JL long and authomatically sends that email

    PLC.py:
    -Connects the other files to the plc so we can get informations from it
    -Needs the jsonfile.json to get info for each station

