from policies.policy import Policy, Action

class FCFSPolicy(Policy):
    """
    First Come First Serve Policy
    Elevator will (directly) go to the first floor that was requested,
    then then it will go to the closest destination in the same direction and carries out until done.
    """
    def __init__(self):
        self.prevAction = Action.Wait
        self.nextDirection = 0 # Direction that will be taken once reached target (0 = no direction, 1 = up, -1 = down)
        self.futureTargets = [] # [[target, direction], ...]]

    def _decide(self, currentFloor, floorButtons, elevatorButtons, elevators, elevator):
        """
        Determine what action the elevator should take
        """
        action = Action.Wait

        if (self.prevAction == Action.WaitUp):
            action = Action.MoveUp
        elif (self.prevAction == Action.WaitDown):
            action = Action.MoveDown
        elif (elevator.target == currentFloor or elevator.target == -1):
            # Action is Wait, Up or Down and elevator has reached target or is idle, set new target

            action = self.prevAction
            target, direction = self._setNextTarget(floorButtons, elevatorButtons, elevator, currentFloor)

            if (target != -1 and direction != 0):
                # New target in different floor, move
                if (target == currentFloor or target == -1):
                    # Wait if target is current floor or no target
                    action = Action.WaitOpen
                elif (target > currentFloor):
                    # Wait to go up if target is above current floor, let passengers in that want to go up
                    action = Action.WaitUp
                else:
                    # Wait to go down if target is below current floor, let passengers in that want to go down
                    action = Action.WaitDown
            else:
                # No new target or target is current floor, wait
                action = Action.WaitOpen
                
            elevator.target = target
        elif (self.prevAction == Action.MoveUp):
            # Not reached target yet, continue moving up
            action = Action.MoveUp
        elif (self.prevAction == Action.MoveDown):
            # Not reached target yet, continue moving down
            action = Action.MoveDown

        # Safeguarding - Change direction if error occurred
        if ((action == Action.MoveDown or action == Action.WaitDown) and currentFloor == elevator.minFloor):
            print(f"WARNING: Elevator tried {action} from min floor {currentFloor}, {elevator.target}")
            action = Action.MoveUp
        elif ((action == Action.MoveUp or action == Action.WaitUp) and currentFloor == elevator.maxFloor):
            print(f"WARNING: Elevator tried {action} from max floor")
            action = Action.MoveDown

        self.prevAction = action
        return action
    
    def _setNextTarget(self, floorButtons, elevatorButtons, elevator, currentFloor):
        """
        Set next target for elevator, returns [target, direction]
        """
        target = -1
        direction = 0

        # Process newly pressed elevatorButtons
        self._updateFutureTargets(elevatorButtons, elevator, currentFloor)
        
        # Check if there are still future targets (of passengers in elevator)
        if (len(self.futureTargets) > 0):
            target, direction = self.futureTargets[0]
            self.nextDirection = direction
            self.futureTargets = self.futureTargets[1:]
        else:
            # Check if there are passengers (outside of elevator) waiting
            for i, button in enumerate(floorButtons):
                if (button.moveUp or button.moveDown):
                    target = i
                    direction = 1 if button.moveUp else -1
                    break
        
        self.target = target
        return [target, direction]
    
    def _checkTarget(self, target):
        """
        Check if target is already in futureTargets
        """
        for t, _ in self.futureTargets:
            if (t == target):
                return True
        return False
    
    def _updateFutureTargets(self, elevatorButtons, elevator, currentFloor):
        """
        Determine new targets for elevator and update futureTargets accordingly
        Returns amount of new targets
        """
        newTargets = []
        # Check if passengers with new target are in elevator
        for i, button in enumerate(elevatorButtons):
            if (button and not self._checkTarget(i)):
                newTargets.append(i)

        # If no new targets, return
        if (not newTargets):
            return 0
        
        # Add new targets (due to FCFS as last priority) to futureTargets
        newTargets.sort()
        lastTarget = self.futureTargets[-1][0] if (len(self.futureTargets) > 0) else currentFloor
        lastDirection = self.futureTargets[-1][1] if (len(self.futureTargets) > 0) else 1 # Prefer up if empty

        # Split array into two parts (above and below lastTarget)
        firstAbove = -1
        for i in range(len(newTargets)):
            if (newTargets[i] < lastTarget):
                continue
            elif (newTargets[i] > lastTarget):
                firstAbove = i
                break
        
        belowTargets, aboveTargets = [], []

        if (firstAbove == -1):  
            # No targets above lastTarget, add all targets below
            belowTargets = newTargets
        else:
            belowTargets = newTargets[:firstAbove]
            aboveTargets = newTargets[firstAbove:]

        # Sort belowTargets in descending order
        belowTargets.reverse()

        # Create pairs of target and direction for futureTargets
        belowTargetPairs = [[target, -1] for target in belowTargets]
        aboveTargetPairs = [[target, 1] for target in aboveTargets]

        if (elevator.minFloor in belowTargets):
            # If minFloor is in belowTargets, change direction of last belowTarget
            belowTargetPairs[-1][1] = 1
        elif (elevator.maxFloor in aboveTargets):
            # If maxFloor is in aboveTargets, change direction of last aboveTarget
            aboveTargetPairs[-1][1] = -1

        if (lastDirection == 1):
            # If last direction was up, add aboveTargets first
            if (belowTargetPairs and aboveTargetPairs):
                # If we have belowTargets and aboveTargets, change direction of last aboveTarget
                aboveTargetPairs[-1][1] = -1
            elif (belowTargetPairs and self.futureTargets):
                # If we have belowTargets and no aboveTargets, change direction of last futureTarget (if exists)
                self.futureTargets[-1][1] = -1

            self.futureTargets += aboveTargetPairs + belowTargetPairs
        else:
            # If last direction was down, add belowTargets first
            if (aboveTargetPairs and belowTargetPairs):
                # If we have aboveTargets and belowTargets, change direction of last belowTarget
                belowTargetPairs[-1][1] = 1
            elif (aboveTargetPairs and self.futureTargets):
                # If we have aboveTargets and no belowTargets, change direction of last futureTarget (if exists)
                self.futureTargets[-1][1] = 1

            self.futureTargets += belowTargetPairs + aboveTargetPairs
        
        return len(newTargets)