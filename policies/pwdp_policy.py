from policies.policy import Policy, Action

class PWDPPolicy(Policy):
    """
    PWDP Policy (Parameterized Weighted Decision Policy)
    Policy which gives each pair of (target, targetDestination)
    or in other words (floor, directionTakenAtFloor) a score,
    based on parameters weighing the terms as described below:
    - elevatorButtonWeight: Elevator button pressed
    - floorButtonWeight:    Floor button pressed
    - directionWeight:      Weight of amount of buttons pressed above or below
    - distanceWeight:       Distance to target
    - distanceExponent:     Exponent for distance
    - timeWeight:           Time since button was pressed

    The score for the i-th floor advertising [Up/Down] is calculated as follows:
    A = elevatorButtonWeight * elevatorButtons[i]
    B = timeWeight * timeSinceElevatorButtonPressed(i) / maxElevatorButtonTime
    C = floorButtonWeight * floorButtons[i].move[Up/Down]
    D = directionWeight * (floorButtonsPressed[Above/Below]) / (totalFloorButtonsPressed)
    E = distanceWeight^(distanceExponent) * abs(currentFloor - i)

    Then the i-th floor advertising [Up/Down] will have score:
    Score = A + B + D + C - E

    Also: The elevator will always follow the direction it advertised
    """
    
    def __init__(self, elevatorButtonWeight=1, floorButtonWeight=1, directionWeight=1, distanceWeight=1, distanceExponent=1, timeWeight=1):
        self.prevAction = Action.Wait
        self.elevatorButtonWeight = elevatorButtonWeight
        self.floorButtonWeight = floorButtonWeight
        self.directionWeight = directionWeight
        self.distanceWeight = distanceWeight
        self.distanceExponent = distanceExponent
        self.timeWeight = timeWeight
        self.elevatorButtonLastPressed = None
        self.minElevatorButtonTime = 0

    def _decide(self, currentFloor, floorButtons, elevatorButtons, elevators, elevator, time):
        """
        Choose action based on floor scores
        """
        action = Action.Wait

        if (self.prevAction in (Action.WaitUp, Action.WaitDown, Action.WaitOpen, Action.Wait)):
            # Get new decision if elevator leaves a target or is idle
            actionToDirection = {
                Action.Wait: 0,
                Action.WaitOpen: 0,
                Action.WaitDown: -1,
                Action.WaitUp: 1
            }

            # Update last pressed elevator button times
            self._updateLastPressedTime(elevatorButtons, time)

            # Get advertised direction from previous action
            advertisedDirection = actionToDirection.get(self.prevAction, 0)
            
            # Get closest target in advertised direction
            target, targetDirection = self._getHighestScoredTarget(currentFloor, floorButtons, elevator, elevatorButtons, time, advertisedDirection)
            elevator.target = target
            elevator.targetDirection = targetDirection

            if (target != -1 and targetDirection != 0):
                # New target in different floor, move
                action = Action.MoveUp if (target > currentFloor) else Action.MoveDown
            else:
                # No new target or target is current floor, wait
                action = Action.Wait
        elif (elevator.target == currentFloor or elevator.target == -1):
            # Elevator has reached target or is idle, wait up or down
            if (elevator.targetDirection == 1):
                # Arrived at target, advertise up
                action = Action.WaitUp
            elif (elevator.targetDirection == -1):
                # Arrived at target, advertise down
                action = Action.WaitDown
            else:
                # We arrived at target, but have no further targets, wait
                action = Action.WaitOpen
        elif (self.prevAction == Action.MoveUp):
            # Not reached target yet, continue moving up
            action = Action.MoveUp
        elif (self.prevAction == Action.MoveDown):
            # Not reached target yet, continue moving down
            action = Action.MoveDown

        self.prevAction = action
        return action
    
    def _updateLastPressedTime(self, elevatorButtons, time):
        """
        Update last pressed elevator button times
        """
        self.time = time
        if (self.elevatorButtonLastPressed == None):
            # Initialize elevatorButtonLastPressed
            self.elevatorButtonLastPressed = [-1] * len(elevatorButtons)
            self.elevatorButtonMaxTime = 0

        for i in range(len(elevatorButtons)):
            if (elevatorButtons[i]):
                self.elevatorButtonLastPressed[i] = time
                self.minElevatorButtonTime = min(self.minElevatorButtonTime, time)
            else:
                self.elevatorButtonLastPressed[i] = -1

    def _timeSinceElevatorButtonPressed(self, i, time):
        """
        Get time since elevator button was pressed, returns 0 if button was not pressed
        """
        return (self.elevatorButtonLastPressed[i] - time) if (self.elevatorButtonLastPressed[i] != -1) else 0

    def _getHighestScoredTarget(self, currentFloor, floorButtons, elevator, elevatorButtons, time, advertisedDirection):
        """
        Get the highest scored `[target, targetDirection]` in the advertised direction, returns `[target, targetDirection]`
        """
        
        # Get all scores for each target and targetDirection
        scores = self._getScores(currentFloor, floorButtons, elevator, elevatorButtons, time, advertisedDirection)

        highestScore = -1
        highestTarget = -1
        highestTargetDirection = 0

        for target, targetDirection, score in scores:
            if (score > highestScore):
                highestScore = score
                highestTarget = target
                highestTargetDirection = targetDirection

        return highestTarget, highestTargetDirection
    
    def _getScores(self, currentFloor, floorButtons, elevator, elevatorButtons, time, advertisedDirection):
        """
        Get all scores for each target and targetDirection, returns `[(target, targetDirection, score)]`
        """
        scores = []

        # Get all scores for each target and targetDirection
        for target in range(len(floorButtons)):
            if (advertisedDirection == 1 and target <= currentFloor):
                continue
            elif (advertisedDirection == -1 and target >= currentFloor):
                continue
            elif (target == currentFloor):
                continue
            for targetDirection in (-1, 1):
                score = self._getScore(currentFloor, floorButtons, elevator, elevatorButtons, target, targetDirection, time)
                scores.append((target, targetDirection, score))
        
        return scores

    def _getScore(self, currentFloor, floorButtons, elevator, elevatorButtons, target, targetDirection, time):
        """
        Get score for target and targetDirection
        """
        floorButtonBool = floorButtons[target].moveUp if (targetDirection == 1) else floorButtons[target].moveDown
        floorButtonsPressed = 0
        totalFloorButtonsPressed = 0
        maxElevatorButtonTime = time - self.minElevatorButtonTime if (self.minElevatorButtonTime != 0) else 1

        for i in range(len(floorButtons)):
            if (floorButtons[i].moveUp or floorButtons[i].moveDown):
                totalFloorButtonsPressed += 1
                if (i > target):
                    floorButtonsPressed += floorButtons[i].moveUp + floorButtons[i].moveDown

        A = self.elevatorButtonWeight * elevatorButtons[target]
        B = self.timeWeight * self._timeSinceElevatorButtonPressed(target, time) / maxElevatorButtonTime
        C = self.floorButtonWeight * floorButtonBool
        D = self.directionWeight * (floorButtonsPressed) / (totalFloorButtonsPressed)
        E = abs(currentFloor - target) * self.distanceWeight ** (self.distanceExponent)
        return A + B + D + C - E
