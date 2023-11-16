import random
import sys


class Passenger():
    def __init__(self, startTime, startLevel, endLevel):
        self.id = random.randint(0, sys.maxsize)
        self.startLevel = startLevel
        self.currentLevel = startLevel
        self.endLevel = endLevel
        self.startTime = startTime

        