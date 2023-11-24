from debug import Debug as DB

from enum import Enum

class Action(Enum):
    MoveDown = -2   # Move down
    WaitDown = -1   # Let passengers enter, which want to go down   
    Wait = 0        # Doors closed, wait for policy to make a decision
    WaitUp = 1      # Let passengers enter, which want to go up
    MoveUp = 2      # Move up
    WaitOpen = 3    # Open doors, let passengers enter/exit no matter the direction


class Policy():
    """
    Base class for all policies, contains the interface for the policy without logic
    """
    def __init__(self):
        self.prevAction = Action.Wait
        pass
    def __str__(self) -> str:
        return DB.str("Class","Policy",kwargs=[self.prevAction],desc=["prevAction"])


    def getAction(self, currentFloor, floorList, elevatorButtons, elevators, elevator):
        """
        Returns the action the elevator should take
        """
        floorButtons = []
        for floor in floorList:
            floorButtons.append(floor.buttonPressed)

        out = self._decide(currentFloor, floorButtons, elevatorButtons, elevators, elevator)

        if (DB.pcyActionUpdate):
            DB.pr("Func","getAction",message="function was called",kwargs=[out],desc=["action"])
        if ((not DB.pcyActionUpdate) and DB.pcyActionUpdateSelect and (out.value in DB.pcyActionUpdateSelection)):
            DB.pr("Func","getAction",message="function was called",kwargs=[out],desc=["action"])

        ''' TODO: Move this to debug.py
        str = f"Elevator {elevator.elevatorIndex} on \033[93mFloor: {currentFloor}\033[0m with {len(elevator.passengerList)} passengers, pAction: {elevator.decision}, Target: {elevator.target} \n  Floors: ["
        for floor in floorList:
            suffix = ""
            if len(floor.passengerList) > 0:
                up = 0
                down = 0
                for p in floor.passengerList:
                    if (p.endLevel > floor.number):
                        up += 1
                    else:
                        down += 1
                cUp = "94m" if up > 0 else "0m"
                cDown = "92m" if down > 0 else "0m"

                suffix = f"\033[{cDown}{down}\033[0m/\033[{cUp}{up}\033[0m"
            else:
                suffix = "0/0"
            str += f"{floor.number}:"+suffix+", "
        print(str[0:-2] + "]")
        '''

        return out
    
    def _decide(self, currentFloor, floorButtons, elevatorButtons, elevators, elevator):
        """
        Internal implementation of how the policy decides what action to take
        """
        action = Action.Wait
        
        # Policy logic goes here

        self.prevAction = action
        return Action.Wait

