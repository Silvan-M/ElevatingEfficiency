import csv
import statistics
from enum import Enum

class Objective(Enum):
    AWT = 0 # average waiting time
    AWTSD = 1 # average waiting time's standard deviation
    ACE = 2 # average crowdedness in elevator

class SimulationStatistics():
    
    def __init__(self, simulation):
        self.finishedTasks = {}

        simulation.building.onPassengerCreated.add_listener(self.onPassengerCreated)
        for e in simulation.building.elevators:
            e.onPassengerEntered.add_listener(self.onPassengerEntered)
            e.onPassengerExited.add_listener(self.onPassengerExited)

    def onPassengerCreated(self, passenger, time):
        self.finishedTasks[passenger.id] = FinishInfo(passenger.id, passenger.startLevel, passenger.endLevel, passenger.startTime)

    def onPassengerEntered(self, passenger, time):
        self.finishedTasks[passenger.id].waitingTime = time - passenger.startTime

    def onPassengerExited(self, passenger, time):
        self.finishedTasks[passenger.id].totalTime = time - passenger.startTime
    
    def writeToFile(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['PassengerID', 'Start', 'Target', 'StartTime', 'WaitingTime', 'TotalTime']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for task in self.finishedTasks.values():
                writer.writerow({'PassengerID': task.id,
                                    'Start': task.start,
                                    'Target': task.target,
                                    'StartTime': task.startTime,
                                    'WaitingTime': task.waitingTime,
                                    'TotalTime': task.totalTime})

    def calculateAverageWaitingTime(self):
        waiting_times = [task.waitingTime for task in self.finishedTasks.values() if task.waitingTime >= 0]
        return statistics.mean(waiting_times) if waiting_times else None

    def calculateStdDevWaitingTime(self):
        waiting_times = [task.waitingTime for task in self.finishedTasks.values() if task.waitingTime >= 0]
        return statistics.stdev(waiting_times) if len(waiting_times) > 1 else None
    
    def getObjective(self,obj : Objective):
        
        if (obj == Objective.AWT):
            return self.calculateAverageWaitingTime
        elif (obj == Objective.AWTSD):
            return self.calculateStdDevWaitingTime
    
    def clearHistory(self):
        self.finishedTasks={}


class FinishInfo():
    def __init__(self, id, start, target, startTime):
        self.id = id
        self.start = start
        self.target = target
        self.startTime = startTime
        self.waitingTime = -1
        self.totalTime = -1
        

    