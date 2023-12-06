from debug import Debug as DB

import random
import numpy as np
from enum import Enum

class FloorDistribution():
    """
    A distribution of how many passengers per floor at a fixed time point.
    """
    def __init__(self, distribution: list):
        self.distribution = distribution

    def __str__(self) -> str:
        return DB.str("Class","Distribution",kwargs=[self.distribution],desc=["distribution"])

    def updateDistribution(self, distribution):
        self.distribution = distribution

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
    
    def getRandomIndex(self, exclude=None):
        indices = [i for i, _ in enumerate(self.distribution) if i != exclude]
        weights = [self.distribution[i] for i in indices]
        index = random.choices(indices, weights=weights, k=1)[0]
        if (DB.dsrFctRandomIndex):
            DB.pr("Func","getRandomIndex",message="function called",kwargs=[index],desc=["return value"])
        return index
        
class EqualFloorDistribution(FloorDistribution):
    """
    A distribution with equal probability for every floor.
    """
    def __init__(self, amountFloors: int):
        self.distribution = []
        for _ in range(amountFloors):
            self.distribution.append(1.0/amountFloors)

class PeakFloorDistribution(FloorDistribution):
    """
    A distribution with a peak probability for a specific floor.
    """
    def __init__(self, amountFloors: int, peakFloor: int, multiplier: int):
        self.distribution = []
        for _ in range(amountFloors):
            self.distribution.append(1.0/amountFloors)
        self.distribution[peakFloor] = self.distribution[peakFloor] * multiplier
        
class TimeDistribution:
    """
    A probability distribution of how many passengers spawn on a floor over time. 
    """
    def __init__(self, timeType, maxTimeTyped, data):
        self.data = []
        self.probabilities = None
        self.lookup_table = None
        self.maxTime = maxTimeTyped
        newData = []

        for (time, probability) in data:
            if timeType == "m":
                time = time * 60
                self.maxTime = maxTimeTyped * 60
            elif timeType == "h":
                time = time * 60 * 60
                self.maxTime = maxTimeTyped * 60 * 60
            newData.append((time, probability))
        
        self.lookup_table = [0] * self.maxTime  # Initialize lookup table with zeros
        
        self.addData(newData)

    def addData(self, data):
        self.data.extend(data)
        times, people = zip(*self.data)
        self.probabilities = people
        self.maxTimePoint = max(times)
        self.precompute_interpolated_probs()

    def precompute_interpolated_probs(self):
        times, _ = zip(*self.data)
        for time in range(0, self.maxTime):
            self.lookup_table[time] = np.interp(time, times, self.probabilities)

    def getInterpolatedProb(self, time):
        out = self.lookup_table[time%self.maxTime]
        if (DB.tdsrFctInterpolatedProb):
            DB.pr("Func","getInterpolatedProb",message="function called",kwargs=[out],desc=["return value"])
        return out


class TimeSpaceDistribution():
    """
    A distribution of how many passengers spawn on every floor over time.
    maxPassengers: The maximum amount of passengers that can spawn in the entire building once.
    timeType: The type of the time values. Can be "s", "m" or "h".
    data: A list of tuples (time, spawnDistribution, targetDistribution) with the last two parameters being a Distribution object.
    timeDistribution: A TimeDistribution object that determines how many passengers spawn in the building at a given time.

    Note: The spawnDistribution and targetDistribution of the data parameter contain the probabilities of which floor should be chosen for spawning or as a target.
    """
    def __init__(self, maxPassengers, timeType, maxTimeTyped, data, timeDistribution, distributionName = "Base distribution"):
        self.floorSpawnDistribution = []
        self.floorTargetDistribution = []
        self.timeDistribution = timeDistribution
        self.times = []
        self.probabilities = None
        self.maxPassengers = maxPassengers
        self.maxTimeTyped = maxTimeTyped
        self.floorAmount = 0
        self.distributionName = distributionName

        if timeType == "m":
            self.maxTime = maxTimeTyped * 60
        elif timeType == "h":   
            self.maxTime = maxTimeTyped * 60 * 60
        else:
            self.maxTime = maxTimeTyped

        if timeType == "m":
            self.maxTime = maxTimeTyped * 60
        elif timeType == "h":   
            self.maxTime = maxTimeTyped * 60 * 60
        else:
            self.maxTime = maxTimeTyped

        # Create reusable empty floor distributions (to save memory)
        self.distribution1 = FloorDistribution([])
        self.distribution2 = FloorDistribution([])

        # Raise Exception if the data is null
        if data is None:
            raise Exception("Data cannot be null.")

        # Sort the data by time, set maxTime and floorAmount
        data.sort(key=lambda x: x[0])
        self.floorAmount = len(data[0][1].distribution)

        # Check if every distribution has the same amount of floors
        for (_, spawnDistribution, timeDistribution) in data:
            if len(spawnDistribution.distribution) != len(timeDistribution.distribution) or \
               len(spawnDistribution.distribution) != self.floorAmount:
                raise Exception("Every distribution needs to have the same amount of floors.")
        
        # Create time distributions for every floor
        for i in range(self.floorAmount):
            floorSpawnTuples = [(tupel[0], tupel[1].distribution[i]) for tupel in data]
            floorTargetTuples = [(tupel[0], tupel[2].distribution[i]) for tupel in data]

            self.floorSpawnDistribution.append(TimeDistribution(timeType, maxTimeTyped, floorSpawnTuples))
            self.floorTargetDistribution.append(TimeDistribution(timeType, maxTimeTyped, floorTargetTuples))
        
    def getPassengersToSpawn(self, time):
        """
        Returns a list of tuples (spawnFloor, targetFloor) of the passengers that spawn at the given time.
        """
        floorSpawnDistribution, floorTargetDistribution = self.getFloorDistributions(time)
        
        # Get the amount of passengers that spawn at the given time
        amount = self.getSpawnAmount(time)

        # Get the spawn and target floor for every passenger
        spawnPassengers = []
        
        for _ in range(amount):
            # Get the spawn and target floor
            spawnFloor = floorSpawnDistribution.getRandomIndex()

            # Get the target floor, exclude the spawn floor
            targetFloor = floorTargetDistribution.getRandomIndex(spawnFloor)

            spawnPassengers.append((spawnFloor, targetFloor))

        return spawnPassengers
        
    def getFloorDistributions(self, time):
        """
        Returns a list of tuples (spawnDistribution, targetDistribution) of the passengers that spawn at the given time.
        """
        # Get the probabilities of the floor distributions, use reusable to save memory
        self.distribution1.updateDistribution([floor.getInterpolatedProb(time) for floor in self.floorSpawnDistribution])
        self.distribution2.updateDistribution([floor.getInterpolatedProb(time) for floor in self.floorTargetDistribution])

        return self.distribution1, self.distribution2
    
    def getNumPassengersTime(self, time):
        """
        Returns a double amount of the passengers that spawn at the given time.
        """
        return self.timeDistribution.getInterpolatedProb(time)*self.maxPassengers

    def getSpawnAmount(self, time):
        """
        Returns an integer amount of passengers that spawn at the given time using the exponential distribution.
        """
        # Get the interpolated probability of the time distribution
        amountOfPassengers = self.getNumPassengersTime(time)

        # Use the exponential distribution to get the amount of passengers that spawn (for maxPassengers < 1)
        random_value = round(np.random.exponential(scale=amountOfPassengers))
        return random_value
    
