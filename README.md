This repository serves the purpose of storing the files from the scheduler.

Here is an explanation of each file: 
    checkParts.py:
    - checks when a part is made on JL Long line and saves it into a postgres database (all info for it is on the code)
    - Later this will be able to connect the database with excel and make some good graphs showing how well parts are being made
    
    main.py:
    - Has the functions to read the signals from the PLC for stations that have a reliable 'part made' signal (JLLONG, CD4, ELCV etc) and saves them on the excel file 
    
    alternativeCount.py:
    - Very similar to main.py. it has the functions to read the signals from the PLC for stations that DON'T have a reliable 'part made' signal (P1, P2, P3, schuller) 

    PLC.py:
    -Connects the other files to the plc so we can get informations from it
    -Needs the jsonfile.json to get info for each station

    run.py
    - the file used to run all the station monitoring. It uses multiprocessing to call the main.py and alternativeCount.py functions to monitor all the stations. 

    emailSending.py
    - Sends the excel file on an email to anyone mentioned on the file 

    DataSheet.xlsx
    - An excel file that reads from the database and creates a graph using VBA to visualize the times each part took to make. It only works for JLLong so far.

    Master_table.xlsx
    - The template week table for the shift report. It is saved so every monday it resets the working table to this one

    workingTable/shifts_table.xlsx
    - Is on a specific folder so we understand that this is the one being edited this week. Every monday after the day shift it will reset this table to the blank master table

    testing.py
    - Used to test the signals from the PLC

    sandBox.py
    - used to test random stuff before adding it to the main code

