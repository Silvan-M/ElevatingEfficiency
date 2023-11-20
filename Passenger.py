import random
import sys

from debug import Debug as DB

class Passenger():
    def __init__(self, startTime, startLevel, endLevel):
        self.id = random.randint(0, sys.maxsize)
        self.startLevel = startLevel
        self.currentLevel = startLevel
        self.endLevel = endLevel
        self.startTime = startTime


    def __str__(self) -> str:
        return DB.str("File","Passenger",kwargs=[self.startLevel,self.currentLevel,self.endLevel,self.startTime,self.id],desc=["starting level","current level","target level", "start time","id"])
    