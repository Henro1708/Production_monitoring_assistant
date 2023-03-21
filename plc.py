import pylogix
from pylogix import PLC
import time
import json
import pdb


class station:

    def __init__(self, name):
        self.name = name

    # Find IP address for avialble station
    def selectIP(self):
        station_Available, data = station.openJson()
        for k in data["station_Detail"]:
            if k["Station_Name"] == self.name:
                ipAdd = k["Station_IPadd"]
                self.ipAdd = ipAdd
        return self.ipAdd 
    
    # Read PLC tag
    def readPLC(self,attribute,tagName, index):
    
        with PLC(self.ipAdd) as comm:
            ret = comm.Read(tagName)
            # print ("{}:{} ({}) = {}".format(self.name, attribute, index, int(ret.Value)))
            response = [self.name,attribute, index, ret.Value]
            return response

    # Find name of program inside one PLC
    def programList(self):
        with PLC(self.ipAdd) as comm:
            programs = comm.GetProgramsList()
            print(programs.Value)

    # Find Tag inside the program inside one PLC
    def programTagList(self, programName):
        with PLC(self.ipAdd) as comm:
            program_tags = comm.GetProgramTagList(programName)
            for t in program_tags.Value:
                print("Tag:", t.TagName, t.DataType)

    # Set Json file communication
    def openJson():   
        station_Available = ["OP090","OP010"]
        with open("jsonfile.json","r") as f:
            data = json.loads(f.read())
        f.close()
        return (station_Available, data)
     
    # LC tag value for station being called
    def lcTag(self):
        attribute = "Light_Curtain"
        station_Available, data = station.openJson()
        for i in station_Available:
            for j in data["station_Detail"]:
                if j["Station_Name"] == self.name:
                    lightCurtain = j["Tag_Name"]["Light_Curtain"]
        output = []
        for index, tagName in enumerate(lightCurtain, start=1):
            value = station.readPLC(self,attribute,tagName, index)
            output.append(value)
        print(output)
        return lightCurtain
    
    # Swipe_Button tag value for station being called
    def swipeButton(self):
        attribute = "Swipe_Button"
        station_Available, data = station.openJson()
        for i in station_Available:
            for j in data["station_Detail"]:
                if j["Station_Name"] == self.name:
                    swipeButton = j["Tag_Name"]["Swipe_Button"]
        output = []
        for index, tagName in enumerate(swipeButton, start=1):
            value = station.readPLC(self,attribute,tagName, index)
            output.append(value)
        print(output)
        return output
    
    # Robot Auto or not tag value for station being called
    def robotAuto(self):
        attribute = "Robot_Auto"
        station_Available, data = station.openJson()
        for i in station_Available:
            for j in data["station_Detail"]:
                if j["Station_Name"] == self.name:
                    robotAuto = j["Tag_Name"]["Robot_Auto"]
        output = []
        for index, tagName in enumerate(robotAuto, start=1):
            value = station.readPLC(self,attribute,tagName, index)
            output.append(value)
        print(output)
        return output
    
    # Robot is running or not tag value for station being called
    def robotRunning(self):
        attribute = "Robot_Running"
        station_Available, data = station.openJson()
        for i in station_Available:
            for j in data["station_Detail"]:
                if j["Station_Name"] == self.name:
                   robotRunning = j["Tag_Name"]["Robot_Running"]
        output = []
        for index, tagName in enumerate(robotRunning, start=1):
            value = station.readPLC(self,attribute,tagName, index)
            output.append(value)
        print(output)
        return output
    
    # Safety Door is closed or not tag value for station being called
    def safetyGate(self):
        attribute = "Safety_Gate"
        station_available, data = station.openJson()
        for i in station_available:
            for j in data["station_Detail"]:
                if j["Station_Name"] == self.name:
                    safetyGate = j["Tag_Name"]["Safety_Gate"]
        output = []
        for index, tagName in enumerate(safetyGate, start=1):
            value = station.readPLC(self,attribute,tagName, index)
            output.append(value)
        print(output)
        return output

    def onePart(self):
        attribute = "One_Part_Trigger"
        station_Available, data = station.openJson()
        for i in station_Available:
            for j in data["station_Detail"]:
                if j["Station_Name"] == self.name:
                    onePart = j["Tag_Name"]["One_Part_Trigger"]
        output = []
        for index, tagName in enumerate(onePart, start=1):
            value = station.readPLC(self,attribute,tagName, index)
            output.append(value)
        #print(output)
        return output
    
    def prodCounter(self):
        attribute = "Production_Counter"
        station_Available, data = station.openJson()
        for i in station_Available:
            for j in data["station_Detail"]:
                if j["Station_Name"] == self.name:
                    prodCounter = j["Tag_Name"]["Production_Counter"]
        output = []
        for index, tagName in enumerate(prodCounter, start=1):
            value = station.readPLC(self,attribute,tagName, index)
            output.append(value)
        #print(output)
        return output
    

    def prodHourCounter(self):
        attribute = "Production_Hourly_Counter"
        station_Available, data = station.openJson()
        for i in station_Available:
            for j in data["station_Detail"]:
                if j["Station_Name"] == self.name:
                    prodHourCounter = j["Tag_Name"]["Production_Hourly_Counter"]
        output = []
        for index, tagName in enumerate(prodHourCounter, start=1):
            value = station.readPLC(self,attribute,tagName, index)
            output.append(value)
        #print(output)
        return output

    def __str__(self):
        return f"[{self.name}]"

