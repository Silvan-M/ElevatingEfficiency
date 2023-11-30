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

    def _decide(self, currentFloor, floorButtons, elevatorButtons, elevators, elevator, time):
        action = Action.Wait
        
        if (not self._hasRequests(floorButtons, elevators, elevatorButtons)):
            # No requests, wait
            action = Action.Wait
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
                print(f"Change direction {elevator.elevatorIndex}")
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
