from policies.policy import Policy, Action

class SCANPolicy(Policy):
    """
    SCAN Policy
    Move up and down, stop at every floor if someone is waiting
    Change direction if reached top or bottom floor
    """
    def __init__(self):
        self.prevAction = Action.Wait
        self.goingUp = True

    def _decide(self, currentFloor, floorButtons, elevatorButtons, elevators, elevator):
        action = Action.WaitOpen
        
        if (not self._hasRequests(floorButtons, elevatorButtons)):
            # No requests, wait
            action = Action.WaitOpen
        elif (self.goingUp):
            # Going up
            if (currentFloor == elevator.maxFloor):
                # Change direction, since we reached the top floor
                self.goingUp = False
                action = Action.WaitDown
            elif (self.prevAction == Action.WaitUp):
                # Waited on floor, now move up
                action = Action.MoveUp
            elif (floorButtons[currentFloor].moveUp or elevatorButtons[currentFloor]):
                # Wait on floor, since someone wants to go up
                action = Action.WaitUp
            else:
                # No one wants to go up, move up
                action = Action.MoveUp
        else:
            if (currentFloor == elevator.minFloor):
                # Change direction, since we reached the bottom floor
                self.goingUp = True
                action = Action.WaitUp
            elif (self.prevAction == Action.WaitDown):
                # Waited on floor, now move down
                action = Action.MoveDown
            elif (floorButtons[currentFloor].moveDown or elevatorButtons[currentFloor]):
                # Wait on floor, since someone wants to go down
                action = Action.WaitDown
            else:
                # No one wants to go down, move down
                action = Action.MoveDown

        self.prevAction = action
        return action
    
    def _hasRequests(self, floorButtons, elevatorButtons):
        """
        Returns true if there is any passenger waiting
        """
        for floor in floorButtons:
            if (floor.moveUp or floor.moveDown):
                return True
        for button in elevatorButtons:
            if (button):
                return True
        return False