from policies.policy import Policy, Action

class LOOKPolicy(Policy):
    """
    LOOK Policy
    Move up and down, stop at every floor if someone is waiting
    Change direction if no requests in current direction
    """
    def __init__(self):
        self.prevAction = Action.Wait
        self.goingUp = True

    def name() -> str:
        return  "LOOK Policy"

    def _decide(self, currentFloor, floorButtons, elevatorButtons, elevators, elevator, time):
        action = Action.Wait

        hasRequestsAbove = self._hasRequestsAbove(currentFloor, floorButtons, elevatorButtons, elevator)
        hasRequestsBelow = self._hasRequestsBelow(currentFloor, floorButtons, elevatorButtons, elevator)
        
        if (not self._hasRequests(floorButtons, elevators, elevatorButtons)):
            # No requests, wait
            action = Action.WaitOpen
        elif (self.goingUp):
            # Going up
            if ((not hasRequestsAbove) and hasRequestsBelow):
                # Change direction, since no requests above
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
            if ((not hasRequestsBelow) and hasRequestsAbove):
                # Change direction, since no requests below
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
    
    def _hasRequestsAbove(self, currentFloor, floorButtons, elevatorButtons, elevator):
        """
        Returns true if there are requests above the current floor
        """
        for i in range(currentFloor+1, elevator.maxFloor+1):
            if (floorButtons[i].moveUp or floorButtons[i].moveDown or elevatorButtons[i]):
                return True
        return False
    
    def _hasRequestsBelow(self, currentFloor, floorButtons, elevatorButtons, elevator):
        """
        Returns true if there are requests below the current floor
        """
        for i in range(elevator.minFloor, currentFloor):
            if (floorButtons[i].moveUp or floorButtons[i].moveDown or elevatorButtons[i]):
                return True
        return False