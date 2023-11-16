
from enum import Enum

class Action(Enum):
    MoveDown = -2
    WaitUp = -1
    Wait = 0
    WaitDown = 1
    MoveUp = 2


class Policy():
    def __init__(self):
        pass

    def getAction(self, floorList, elevatorButtons):
        floorButtons = []
        for floor in floorList:
            floorButtons.append(floor.buttonPressed)

        return self._decide(floorButtons, elevatorButtons)
    
    def _decide(self, floorButtons, elevatorButtons):
        return Action.Wait
    
    
    
