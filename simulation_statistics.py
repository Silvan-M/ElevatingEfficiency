from plotter import LivePlotter
from plotter import Objective

import matplotlib.pyplot as plt
import csv
import statistics



class SimulationStatistics():
    
    def __init__(self, simulation, plotters):
        self.plotters = plotters
        simulation.onSimulationStarted.add_listener(self.onSimulationStarted)
        self.finishedTasks = {}

    def onSimulationStarted(self, simulation, stepAmount):
        building = simulation.building
        simulation.onStepEnd.add_listener(self.onStepEnd)
        simulation.onSimulationFinished.add_listener(self.onSimulationFinished)
        building.onPassengerCreated.add_listener(self.onPassengerCreated)
        for e in building.elevators:
            e.onPassengerEntered.add_listener(self.onPassengerEntered)
            e.onPassengerExited.add_listener(self.onPassengerExited)

        for p in self.plotters:
            if isinstance(p, LivePlotter):
                p.startPlot(simulation, stepAmount)

    def onStepEnd(self, simulation, time):
        for p in self.plotters:
            if isinstance(p, LivePlotter):
                p.step(simulation, self, time)


    def onSimulationFinished(self, simulation):
        self.writeToFile("results.txt")
        out = self.calculateAverageWaitingTime()
        print("Average waiting time: " + str(out))

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
            return self.calculateAverageWaitingTime()
        elif (obj == Objective.AWTSD):
            return self.calculateStdDevWaitingTime()


class FinishInfo():
    def __init__(self, id, start, target, startTime):
        self.id = id
        self.start = start
        self.target = target
        self.startTime = startTime
        self.waitingTime = -1
        self.totalTime = -1




        

    