import csv
import statistics

class Statistics():
    
    def __init__(self, simulation):
        self.finishedTasks = {}

        simulation.building.passengerCreatedListener.add_listener(self.passengerCreated)
        for e in simulation.building.elevators:
            e.passengerEnteredElevatorListener.add_listener(self.passengerEnteredElevator)
            e.passengerExitedElevatorListener.add_listener(self.passengerExitedElevator)

    def passengerCreated(self, passenger, time):
        self.finishedTasks[passenger.id] = FinishInfo(passenger.startLevel, passenger.endLevel, passenger.startTime)

    def passengerEnteredElevator(self, passenger, time):
        self.finishedTasks[passenger.id].waitingTime = time - passenger.startTime

    def passengerExitedElevator(self, passenger, time):
        self.finishedTasks[passenger.id].totalTime = time - passenger.startTime
    
    def writeToFile(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['PassengerID', 'Start', 'Target', 'StartTime', 'WaitingTime', 'TotalTime']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for task in self.finishedTasks:
                if task.waitingTime >= 0:  # Ignore negative waitingTime
                    writer.writerow({'PassengerID': task.id,
                                     'Start': task.start,
                                     'Target': task.target,
                                     'StartTime': task.startTime,
                                     'WaitingTime': task.waitingTime,
                                     'TotalTime': task.totalTime})

    def calculateAverageWaitingTime(self):
        waiting_times = [task.waitingTime for task in self.finishedTasks if task.waitingTime >= 0]
        return statistics.mean(waiting_times) if waiting_times else None

    def calculateStdDevWaitingTime(self):
        waiting_times = [task.waitingTime for task in self.finishedTasks if task.waitingTime >= 0]
        return statistics.stdev(waiting_times) if len(waiting_times) > 1 else None

class FinishInfo():
    def __init__(self, start, target, startTime):
        self.start = start
        self.target = target
        self.startTime = startTime
        self.watingTime = -1
        self.totalTime = -1
        

    