from policies.policy import Policy, Action

class PWDPPolicy(Policy):
    """
    PWDP Policy (Parameterized Weighted Decision Policy)
    Policy which gives each pair of (target, targetDestination)
    or in other words (floor, directionTakenAtFloor) a score,
    based on parameters weighing the terms as described below:
    - elevatorButtonWeight: Award if elevator button pressed on floor i
    - timeWeight:           Award elevator buttons which were pressed a long time ago
    - floorButtonWeight:    Award floor buttons which were pressed a long time ago
    - directionWeight:      Award high amount of buttons pressed [above/below] floor i
    - competitorWeight:     Penalize direction in which other eleavtors are moving
    - distanceWeight:       Penalize high distance to target
    - distanceExponent:     Exponent for distance penalty

    The score for the i-th floor advertising [Up/Down] is calculated as follows:
    s1 = elevatorButtonWeight * elevatorButtons[i]
    s2 = timeWeight * timeSinceElevatorButtonPressed(i) / maxElevatorButtonTime
    s3 = floorButtonWeight * floorButtons[i].move[Up/Down]*floorButtons[i].timeSincePressed / maxFloorButtonTime
    s4 = directionWeight * (floorButtonsPressed[Above/Below]) / (totalFloorButtonsPressed)
    s5 = competitorWeight * (amountOfElevatorsMoving[Above/Below]) / (totalAmountOfElevators)
    s6 = distanceWeight^(distanceExponent) * abs(currentFloor - i)

    Then the i-th floor advertising [Up/Down] will have score:
    Score = (s1 + s2 + s3 + s4) / max(1, (s5 + s6))

    Also: The elevator will always follow the direction it advertised
    """
    
    def __init__(self, elevatorButtonWeight=1, timeWeight=1, floorButtonWeight=1, directionWeight=1, competitorWeight=1,  distanceWeight=1, distanceExponent=1):
        self.prevAction = Action.Wait
        self.elevatorButtonWeight = elevatorButtonWeight
        self.timeWeight = timeWeight
        self.floorButtonWeight = floorButtonWeight
        self.directionWeight = directionWeight
        self.competitorWeight = competitorWeight
        self.distanceWeight = distanceWeight
        self.distanceExponent = distanceExponent
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
            target, targetDirection = self._getHighestScoredTarget(currentFloor, floorButtons, elevator, elevators, elevatorButtons, time, advertisedDirection)
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

    def _getHighestScoredTarget(self, currentFloor, floorButtons, elevator, elevators, elevatorButtons, time, advertisedDirection):
        """
        Get the highest scored `[target, targetDirection]` in the advertised direction, returns `[target, targetDirection]`
        """
        # Get all scores for each target and targetDirection
        scores = self._getScores(currentFloor, floorButtons, elevator, elevators, elevatorButtons, time, advertisedDirection)

        # Get highest score
        highestTarget = -1
        highestTargetDirection = 0
        highestScore = -1

        for target, targetDirection, score in scores:
            if (score > highestScore):
                highestScore = score
                highestTarget = target
                highestTargetDirection = targetDirection

        return highestTarget, highestTargetDirection
    
    def _getScores(self, currentFloor, floorButtons, elevator, elevators, elevatorButtons, time, advertisedDirection):
        """
        Get all scores for each target and targetDirection, returns `[(target, targetDirection, score)]`
        """
        scores = []

        # Get all scores for each target and targetDirection
        for target in range(len(floorButtons)):
            if (target <= currentFloor and advertisedDirection == 1) or \
                (target >= currentFloor and advertisedDirection == -1):
                # Do not allow targets not in advertised direction
                continue
            elif (target == currentFloor):
                # Do not allow to go to current floor
                continue
            for targetDirection in (-1, 1):
                if (target == elevator.minFloor and targetDirection == -1) or \
                  (target == elevator.maxFloor and targetDirection == 1):
                    # Do not allow to go to floor below minFloor or above maxFloor
                    continue 

                score = self._getScore(currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, targetDirection, time)
                scores.append((target, targetDirection, score))
        
        return scores

    def _getScore(self, currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, targetDirection, time):
        """
        Get score for target and targetDirection
        """
        # Calculate score and firstly get s1, s2, s3, s4, s5, s6
        s1 = self._getS1(currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, targetDirection, time)
        s2 = self._getS2(currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, targetDirection, time)
        s3 = self._getS3(currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, targetDirection, time)
        s4 = self._getS4(currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, targetDirection, time)
        s5 = self._getS5(currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, targetDirection, time)
        s6 = self._getS6(currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, targetDirection, time)

        return (s1 + s2 + s3 + s4) / max(1, (s5 + s6))
    
    def _getS1(self, currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, targetDirection, time):
        """
        Get s1, weighted amount of people in elevator going to target
        """
        return self.elevatorButtonWeight * elevatorButtons[target]
    
    def _getS2(self, currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, targetDirection, time):
        """
        Get s2, weighted time since elevator button of target was pressed 
        """
        # Get max time since elevator button was pressed
        maxElevatorButtonTime = time - self.minElevatorButtonTime if (self.minElevatorButtonTime != 0) else 1

        return self.timeWeight * self._timeSinceElevatorButtonPressed(target, time) / maxElevatorButtonTime
    
    def _getS3(self, currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, targetDirection, time):
        """
        Get s3, weighted amount of people in floor going in targetDirection (in the view of target)
        """
        buttonPressed = floorButtons[target].moveUp if (targetDirection == 1) \
                              else floorButtons[target].moveDown
        buttonPressedSince = time - floorButtons[target].lastPressedUp if (targetDirection == 1) \
                                   else time - floorButtons[target].lastPressedDown

        maxFloorButtonTime = 0

        for i in range(len(floorButtons)):
            if (floorButtons[i].lastPressedDown > maxFloorButtonTime):
                maxFloorButtonTime = time - floorButtons[i].lastPressedDown
            if (floorButtons[i].lastPressedUp > maxFloorButtonTime):
                maxFloorButtonTime = time - floorButtons[i].lastPressedUp

        if (maxFloorButtonTime == 0):
            maxFloorButtonTime = 1

        return self.floorButtonWeight * buttonPressed * buttonPressedSince / maxFloorButtonTime
    
    def _getS4(self, currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, targetDirection, time):
        """
        Get s4, weighted amount of floor buttons pressed (per floor) in targetDirection (in the view of target)
        """
        
        # Get amount of floor buttons pressed above/below (dependant on targetDirection) target and it's total amount
        floorButtonsPressed = 0
        totalFloorButtonsPressed = 0

        for i in range(len(floorButtons)):
            if (i > target and targetDirection == 1) or (i < target and targetDirection == -1):
                totalFloorButtonsPressed += 1
                if (floorButtons[i].moveUp or floorButtons[i].moveDown):
                    # Floor button is pressed in direction targetDirection
                    floorButtonsPressed += floorButtons[i].moveUp + floorButtons[i].moveDown

        if totalFloorButtonsPressed == 0:
            # No floor buttons pressed, set to 1 to avoid division by 0
            totalFloorButtonsPressed = 1

        return self.directionWeight * (floorButtonsPressed) / (totalFloorButtonsPressed)

    def _getS5(self, currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, targetDirection, time):
        """
        Get s5, weighted amount of elevators moving in targetDirection (in the view of target)
        """
        amountOfElevatorsMoving = 0
        totalElevatorsMoving = 0

        for i, e in enumerate(elevators):
            pos = e.target 
            totalElevatorsMoving += 1
            if (pos != -1 and (pos < target and e.targetDirection == 1) or (pos > target and e.targetDirection == -1)):
                if (i > target and targetDirection == 1) or (i < target and targetDirection == -1):
                    # Elevator is moving in direction targetDirection
                    amountOfElevatorsMoving += 1

        if totalElevatorsMoving == 0:
            # No elevators moving, set to 1 to avoid division by 0
            totalElevatorsMoving = 1

        return self.competitorWeight * amountOfElevatorsMoving / totalElevatorsMoving
    
    def _getS6(self, currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, targetDirection, time):
        """
        Get s6, weighted distance to target
        """
        return abs(currentFloor - target) * self.distanceWeight ** (self.distanceExponent)

    def _printScores(self, scores, amountOfFloors):
        """
        Print scores for each target and targetDirection
        """
        titleLine = "T: "
        firstLine = "U: "
        secondLine = "D: "

        scoreU = [0]*amountOfFloors
        scoreB = [0]*amountOfFloors

        for target, targetDirection, score in scores:
            if (targetDirection == 1):
                scoreU[target] = score
            else:
                scoreB[target] = score
        
        for i in range(amountOfFloors):
            titleLine += f"{i:6d} "
            firstLine += f"{scoreU[i]:6.2f} " if (scoreU[i] != 0) else "       "
            secondLine += f"{scoreB[i]:6.2f} " if (scoreB[i] != 0) else "       "
        
        print(f"{titleLine}\n{firstLine}\n{secondLine}")