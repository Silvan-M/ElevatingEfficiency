import sys
import matplotlib.pyplot as plt
import csv
import statistics
from itertools import groupby
from operator import attrgetter
from enum import Enum

class Objective(Enum):
    AWT = "average waiting time" # average waiting time
    AWTSD = "standard deviation of waiting time" # average waiting time's standard deviation
    ATTD = "average time to destination" # average time to destination
    ACE = "average crowededness" # average crowdedness in elevator
    AMP = "amount of people" # amount of people spawned

class SimulationStatistics():
    
    def __init__(self, simulation):
        simulation.onSimulationStarted.add_listener(self.onSimulationStarted)
        simulation.onStepEnd.add_listener(self.onStepEnd)
        self.finishedTasks = {}
        self.crowdedness = []

    def onSimulationStarted(self, simulation, startTime, stepAmount):
        building = simulation.building
        simulation.onSimulationFinished.add_listener(self.onSimulationFinished)
        building.onPassengerCreated.add_listener(self.onPassengerCreated)
        for e in building.elevators:
            e.onPassengerEntered.add_listener(self.onPassengerEntered)
            e.onPassengerExited.add_listener(self.onPassengerExited)

    def onStepEnd(self, simulation, time):
        building = simulation.building
        count = sum(len(e.passengerList) for e in building.elevators)
        self.crowdedness.append(count / len(building.elevators))

    def onSimulationFinished(self, simulation):
        time = simulation.time
        # Augment data for those who didn't finish in time
        for t in self.finishedTasks:
            val = self.finishedTasks[t]
            if val.waitingTime < 0:
                val.waitingTime = time - val.startTime
            if val.totalTime < 0:         
                val.totalTime = time - val.startTime

        self.writeToFile("results.txt")

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

    def calculateAverageWaitingTime(self, fromTime=-1, toTime=sys.maxsize):
        waiting_times = [task.waitingTime for task in self.finishedTasks.values() if task.startTime >= fromTime and task.startTime <= toTime]
        return statistics.mean(waiting_times) if waiting_times else None

    def calculateStdDevWaitingTime(self, fromTime=-1, toTime=sys.maxsize):
        waiting_times = [task.waitingTime for task in self.finishedTasks.values() if task.startTime >= fromTime and task.startTime <= toTime]
        return statistics.stdev(waiting_times) if len(waiting_times) > 1 else None
    
    def calculateAmountPeopleSpawned(self, fromTime=-1, toTime=sys.maxsize):
        return len([task for task in self.finishedTasks.values() if task.startTime >= fromTime and task.startTime <= toTime])
    
    def calculateAverageTimeToDestination(self, fromTime=-1, toTime=sys.maxsize):
        total_times = [task.totalTime for task in self.finishedTasks.values() if task.startTime >= fromTime and task.startTime <= toTime]
        return statistics.mean(total_times) if total_times else None
    
    def calculateAverageCrowdedness(self, fromTime=-1, toTime=sys.maxsize):
        return statistics.mean(self.crowdedness[fromTime:toTime]) if self.crowdedness else None
    
    def calculateAverageCrowdednessPerFloor(self):
        sorted_finish_info = sorted(self.finishedTasks.values(), key=attrgetter('start'))

        grouped_finish_info = {key: list(group) for key, group in groupby(sorted_finish_info, key=attrgetter('start'))}

        mean_values = {key: statistics.mean(info.totalTime for info in group) for key, group in grouped_finish_info.items()}
        
        return mean_values

    
    def getObjective(self,obj : Objective, timestep=-1, timestepAmount=24):
        maxTime = max([task.startTime for task in self.finishedTasks.values()])
        timestep = maxTime if timestep == -1 else timestep
        result = None

        if (obj == Objective.AWT):
            result = [self.calculateAverageWaitingTime(i*timestep, (i+1)*timestep-1) for i in range((maxTime+timestep-1)//timestep)]
        elif (obj == Objective.AWTSD):
            result = [self.calculateStdDevWaitingTime(i*timestep, (i+1)*timestep-1) for i in range((maxTime+timestep-1)//timestep)]
        elif (obj == Objective.ACE):
            result = [self.calculateAverageCrowdedness(i*timestep, (i+1)*timestep-1) for i in range((maxTime+timestep-1)//timestep)]
        elif (obj == Objective.AMP):
            result = [self.calculateAmountPeopleSpawned(i*timestep, (i+1)*timestep-1) for i in range((maxTime+timestep-1)//timestep)]
        elif (obj == Objective.ATTD):
            result = [self.calculateAverageTimeToDestination(i*timestep, (i+1)*timestep-1) for i in range((maxTime+timestep-1)//timestep)]
        
        while (len(result) < timestepAmount):
            result.append(None)
        return result if timestep != maxTime else result[0]
    
    def getObjectives(self,objs : [Objective], timestep=-1):
        return [self.getObjective(obj, timestep) for obj in objs]

class FinishInfo():
    def __init__(self, id, start, target, startTime):
        self.id = id
        self.start = start
        self.target = target
        self.startTime = startTime
        self.waitingTime = -1
        self.totalTime = -1




        

    