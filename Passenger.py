from Debug import Debug as DB
class Passenger():
    def __init__(self, startTime, startLevel, endLevel):
        self.startLevel = startLevel
        self.currentLevel = startLevel
        self.endLevel = endLevel
        self.startTime = startTime


        def __str__(self) -> str:
            return DB.str("File","Passenger",kwargs=[self.startLevel,self.currentLevel,self.endLevel,self.startTime],desc=["starting level","current level","target level", "start time"])
        