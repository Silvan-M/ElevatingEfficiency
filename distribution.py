from debug import Debug as DB

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
        self.maxTime = 0

    def __str__(self) -> str:
        return DB.str("Class","Distribution",kwargs=[self.distribution],desc=["distribution"])


    def isChosen(self, index):
        out = self.getRandomIndex(index) > random.random()
        if (DB.dsrFctIsChosen):
            DB.pr("Func","isChosen",message="function called",kwargs=[out],desc=["return value"])
        return out

    def getIndexProb(self, index):
        out = self.distribution[index]
        if (DB.dsrFctgetIndexProb):
            DB.pr("Func","getIndexProb",message="function called",kwargs=[out],desc=["return value"])
        return out
    
    def getRandomIndex(self, building):
        out = random.choices(building.floors, weights=self.distribution, k=1)[0].number
        if (DB.dsrFctRandomIndex):
            DB.pr("Func","getRandomIndex",message="function called",kwargs=[out],desc=["return value"])

        return out
        

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
        self.maxTime = max(times)

    def getInterpolatedProb(self, time):
        times, _ = zip(*self.data)
        interpolated_probability = np.interp(time%self.maxTime, times, self.probabilities)
        out = interpolated_probability*self.maxPassengers
        if (DB.tdsrFctInterpolatedProb):
            DB.pr("Func","getInterpolatedProb",message="function called",kwargs=[out],desc=["return value"])
        return out
    
    def getRandomProb(self, time):
        mean = self.getInterpolatedProb(time)
        random_value = np.random.exponential(scale=mean)
        return random_value
    
class CustomDistribution(Distribution):
    def __init__(self, distribution: list):
        self.distribution = distribution
