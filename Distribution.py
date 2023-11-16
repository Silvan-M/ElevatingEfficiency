
import random
import numpy as np
from enum import Enum

class DistrType(Enum):
    UNIFORM = 0
    NORMAL = 1
    EXPONENTIAL = 2
    CUSTOM = 3

class Distribution():
    def __init__(self, amountFloors: int, type: DistrType):
        self.distribution = []
        for i in range(amountFloors):
            self.distribution.append(1.0/amountFloors)

    def isChosen(self, index):
        return self.getRandomIndex(index) > random.random()

    def getIndexProb(self, index):
        return self.distribution[index]
    
    def getRandomIndex(self, building):
        return random.choices(building.floors, weights=self.distribution, k=1)[0].number
        

class TimeDistribution:
    def __init__(self, maxPassengers, timeType, data):
        self.data = []
        self.probabilities = None
        self.maxPassengers = maxPassengers

        for (time, people) in data:
            if timeType == "m":
                time = time * 60
            elif timeType == "h":
                time = time * 60 * 60
            self.data.append((time, people))
        self.addData(self.data)

    def addData(self, data):
        self.data.extend(data)
        times, people = zip(*self.data)
        self.probabilities = [p / max(people) for p in people]

    def getInterpolatedProb(self, time):
        times, _ = zip(*self.data)
        interpolated_probability = np.interp(time, times, self.probabilities)
        return interpolated_probability*self.maxPassengers
    
    class CustomDistribution(Distribution):
        def __init__(self, distribution: list):
            self.distribution = distribution