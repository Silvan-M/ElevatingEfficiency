from policies.policy import Policy, Action

class SSTFPolicy(Policy):
    """
    SSTF Policy (Shortest Seek Time First)
    Move to the closest target in the same direction
    """
    
    def __init__(self, prefersElevatorButtons=True):
        self.prevAction = Action.Wait
        self.goingUp = True
        
        # If true, elevator buttons are preferred over external buttons
        self.prefersElevatorButtons = prefersElevatorButtons
    
    def name(self) -> str:
        return  "SSTF Policy"

    def _decide(self, currentFloor, floorButtons, elevatorButtons, elevators, elevator, time):
        """
        Choose action based on advertised direction and closest target
        """
        action = Action.Wait

        if (elevator.target == currentFloor or elevator.target == -1):
            # Get new decision if elevator arrived at target or is idle
            
            # Initilize target
            target, targetDirection = -1, 0

            # Get closest target in advertised direction
            if (self._hasRequests(floorButtons, elevators, elevatorButtons)):
                # Has requests, set new target
                target, targetDirection = self._getClosestTarget(currentFloor, floorButtons, elevatorButtons, elevator.targetDirection)
            
            elevator.target = target
            elevator.targetDirection = targetDirection

            if (target != -1):
                # New target in different floor, move
                action = Action.WaitUp if (target > currentFloor) else Action.WaitDown
            else:
                # No new target or target is current floor, wait
                action = Action.WaitOpen
        elif (self.prevAction in (Action.MoveUp, Action.WaitUp)):
            # Not reached target yet, continue/start moving up
            action = Action.MoveUp
        elif (self.prevAction in (Action.MoveDown, Action.WaitDown)):
            # Not reached target yet, continue/start moving down
            action = Action.MoveDown

        self.prevAction = action
        return action

    def _getClosestTarget(self, currentFloor, floorButtons, elevatorButtons, advertisedDirection):
        """
        Get the closest target in the given advertisedDirection, returns `[target, targetDirection]`
        """
        target = -len(floorButtons)-1 # set to invalid, low enough value
        targetDirection = 0
        
        # Check elevator buttons
        for i, button in enumerate(elevatorButtons):
            if (advertisedDirection == 1 and i <= currentFloor) or \
               (advertisedDirection == -1 and i >= currentFloor) or i == currentFloor:
                # Skip if not in advertised direction or current floor
                continue
            elif (button and abs(i - currentFloor) < abs(target - currentFloor)):
                target = i
        
        if (self.prefersElevatorButtons and target >= 0):
            # If elevator buttons are preferred, return target if found
            return target, 0

        # Check external buttons
        for i, button in enumerate(floorButtons):
            targetDist = abs(target - currentFloor)
            buttonDist = abs(i - currentFloor)

            if (advertisedDirection == 1 and i <= currentFloor) or \
               (advertisedDirection == -1 and i >= currentFloor) or i == currentFloor:
                # Skip if not in advertised direction or current floor
                continue
            elif (button.moveUp and (buttonDist < targetDist)):
                target = i
                targetDirection = 1
            elif (button.moveDown and (buttonDist < targetDist)):
                target = i
                targetDirection = -1
            elif ((button.moveUp or button.moveDown) and (buttonDist == targetDist)):
                # If elevator button has same distance as external button, update with targetDirection
                targetDirection = 1 if button.moveUp else -1

        if (target < 0):
            # No target found, set to -1
            target = -1
            targetDirection = 0
        
        return target, targetDirection