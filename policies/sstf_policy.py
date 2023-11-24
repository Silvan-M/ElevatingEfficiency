from policies.policy import Policy, Action

class SSTFPolicy(Policy):
    """
    SSTF Policy (Shortest Seek Time First)
    Move to the closest target in the same direction
    """
    
    def __init__(self):
        self.prevAction = Action.Wait
        self.goingUp = True

    def _decide(self, currentFloor, floorButtons, elevatorButtons, elevators, elevator):
        pass