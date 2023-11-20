from debug import Debug as DB

from enum import Enum

class Action(Enum):
    MoveDown = -2
    WaitDown = -1
    Wait = 0
    WaitUp = 1
    MoveUp = 2


class Policy():
    def __init__(self):
        self.prevAction = Action.Wait
        pass
    def __str__(self) -> str:
        return DB.str("Class","Policy",kwargs=[self.prevAction],desc=["prevAction"])


    def getAction(self, currentFloor, floorList, elevatorButtons, elevatorList, elevatorIndex):
        floorButtons = []
        for floor in floorList:
            floorButtons.append(floor.buttonPressed)

        out = self._decide(currentFloor, floorButtons, elevatorButtons, elevatorList, elevatorIndex)

        if (DB.pcyActionUpdate):
            DB.pr("Func","getAction",message="function was called",kwargs=[out],desc=["action"])
        if ((not DB.pcyActionUpdate) and DB.pcyActionUpdateSelect and (out.value in DB.pcyActionUpdateSelection)):
            DB.pr("Func","getAction",message="function was called",kwargs=[out],desc=["action"])

          
        return out
    
    def _decide(self, currentFloor, floorButtons, elevatorButtons, elevatorList, elevatorIndex):
        action = Action.Wait
        
        # Policy logic goes here

        self.prevAction = action
        return Action.Wait
    
class BasicPolicy(Policy):
    def __init__(self):
        self.prevAction = Action.Wait
        self.goingUp = True

    def _decide(self, currentFloor, floorButtons, elevatorButtons, elevatorList, elevatorIndex):
        action = Action.Wait
        if (self.goingUp):
            if (currentFloor == len(floorButtons) - 1):
                self.goingUp = False
                action = Action.WaitDown
            elif (self.prevAction == Action.WaitUp):
                action = Action.MoveUp
            elif (floorButtons[currentFloor].moveUp or elevatorButtons[currentFloor]):
                action = Action.WaitUp
            else:
                action = Action.MoveUp
        else:
            if (currentFloor == 0):
                self.goingUp = True
                action = Action.WaitUp
            elif (self.prevAction == Action.WaitDown):
                action = Action.MoveDown
            elif (floorButtons[currentFloor].moveDown or elevatorButtons[currentFloor]):
                action = Action.WaitDown
            else:
                action = Action.MoveDown

        self.prevAction = action
        return action
