from policies.policy import Action
import policies

class PWDPPolicyOptimized(policies.Policy):
    """
    PWDP Policy (Parameterized Weighted Decision Policy)
    Policy which evaluates each floor by giving it a score using the following parameters:
    - elevatorButtonWeight:         Award elevator button pressed on floor i
    - elevatorButtonTimeWeight:     Award elevator buttons which were pressed a long time ago
    - floorButtonWeight:            Award floor buttons which were pressed
    - floorButtonTimeWeight:        Award floor buttons which were pressed a long time ago
    - competitorWeight:             Penalize if other elevators are heading to floor i
    - distanceWeight:               Penalize high distance to target
    - distanceExponent:             Exponent for distance penalty

    The score for the i-th floor advertising [Up/Down] is calculated as follows:
    s1 = elevatorButtonWeight * elevatorButtons[i]
    s2 = elevatorButtons[i] * elevatorButtonWeight * elevatorButtonTimeWeight * (targetButtonTime / max(1, maxElevatorButtonTime))
    s3 = floorButtonWeight * buttonPressed
    s4 = floorButtonWeight * floorButtonTimeWeight * (maxFloorButtonTime[i] / max(maxAllFloorButtonTime, 1))
    s5 = sum(elevatorDistances) * competitorWeight
    s6 = distanceWeight^(distanceExponent) * abs(currentFloor - i)

    Then the i-th floor advertising [Up/Down] will have score:
    Score = (s1 + s2 + s3 + s4) / max(1, (s5 + s6))

    The elevator will then choose the highest scored floor, set it as target, and move to it. 
    Along the way, it will stop at each floor if someone wants to enter or exit the elevator on that floor.
    """
    
    def __init__(self, loadPath='paramOptimizer/save_params.txt'):
        with open(loadPath, "r") as file:
            lines = file.readlines()
            if lines:
                l = lines[-1].strip().split(',')
                
                self.elevatorButtonWeight = (float)(l[1])
                self.elevatorButtonTimeWeight = (float)(l[2])
                self.floorButtonWeight = (float)(l[3])
                self.floorButtonTimeWeight = (float)(l[4])
                self.competitorWeight = (float)(l[5])
                self.distanceWeight = (float)(l[6])
            else:
                print("File is empty.")

        self.prevAction = Action.Wait

        self.distanceExponent = 1
        self.elevatorButtonLastPressed = None

    def name(self) -> str:
        return  "PWDP Policy Optimized"

    def _decide(self, currentFloor, floorButtons, elevatorButtons, elevators, elevator, time):
        """
        Choose action based on floor scores
        """
        action = Action.Wait

        # Update last pressed elevator button times
        self._updateLastPressedTime(elevatorButtons, time)

        if (self.prevAction in (Action.WaitOpen, Action.Wait)):
            # Get new decision if elevator leaves a target or is idle
            action = self._getNewAction(currentFloor, floorButtons, elevatorButtons, elevators, elevator, time)
        elif (self.prevAction in (Action.WaitUp, Action.WaitDown)):
            # All passengers entered, close doors and move
            action = Action.MoveUp if (self.prevAction == Action.WaitUp) else Action.MoveDown
        elif (elevator.target == currentFloor or elevator.target == -1):
            # Elevator has reached target or is idle, get new target
            action = self._getNewAction(currentFloor, floorButtons, elevatorButtons, elevators, elevator, time)
        elif (self.prevAction == Action.MoveUp):
            # Not reached target yet, continue moving up
            action = Action.WaitUp if (floorButtons[currentFloor].moveUp or elevatorButtons[currentFloor]) else Action.MoveUp
        elif (self.prevAction == Action.MoveDown):
            # Not reached target yet, continue moving down
            action = Action.WaitDown if (floorButtons[currentFloor].moveDown or elevatorButtons[currentFloor]) else Action.MoveDown

        self.prevAction = action
        return action
    
    def _getNewAction(self, currentFloor, floorButtons, elevatorButtons, elevators, elevator, time):
        """
        Get the new target floor for the elevator
        """
        target = -1
        
        # Get closest target in advertised direction
        if self._hasRequestsExceptCurrent(floorButtons, elevators, elevatorButtons, currentFloor):
            # There are requests, get highest scored target
            target = self._getHighestScoredTarget(currentFloor, floorButtons, elevator, elevators, elevatorButtons, time)
            
        elevator.target = target

        if (target != -1):
            # New target in different floor, move
            action = Action.WaitUp if (target > currentFloor) else Action.WaitDown
        else:
            # No new target or target is current floor, wait
            action = Action.WaitOpen

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
            if (elevatorButtons[i] and self.elevatorButtonLastPressed[i] == -1):
                self.elevatorButtonLastPressed[i] = time
            elif (not elevatorButtons[i]):
                self.elevatorButtonLastPressed[i] = -1
    
    def _getHighestScoredTarget(self, currentFloor, floorButtons, elevator, elevators, elevatorButtons, time):
        """
        Get the highest scored `[target, targetDirection]` in the advertised direction, returns `[target, targetDirection]`
        """
        # Get all scores for each target
        scores = self._getScores(currentFloor, floorButtons, elevator, elevators, elevatorButtons, time)

        # Get highest score
        highestScoreIndex, _ = max(enumerate(scores), key=lambda x: x[1])
        
        return highestScoreIndex
    
    def _getScores(self, currentFloor, floorButtons, elevator, elevators, elevatorButtons, time):
        """
        Get all scores for each target and targetDirection, returns `[(target, targetDirection, score)]`
        """
        scores = []

        # Get all scores for each target and targetDirection
        for target in range(len(floorButtons)):
            if (target == currentFloor):
                # Do not allow to go to current floor
                scores.append(0)
                continue

            score = self._getScore(currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, time)
            scores.append(score)
        
        return scores
    
    def _getScore(self, currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, time):
        """
        Get score for target and targetDirection
        """
        # Calculate score and firstly get s1, s2, s3, s4, s5, s6
        s1 = self._getS1(currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, time)
        s2 = self._getS2(currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, time)
        s3 = self._getS3(currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, time)
        s4 = self._getS4(currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, time)
        s5 = self._getS5(currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, time)
        s6 = self._getS6(currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, time)

        return (s1 + s2 + s3 + s4) / max(1, (s5 + s6))
    
    def _getS1(self, currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, time):
        """
        Get s1, weighted elevator button at target
        """
        return self.elevatorButtonWeight * elevatorButtons[target]
    
    def _getS2(self, currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, time):
        """
        Get s2, weighted time since elevator button of target was pressed 
        """
        # Calculate the time since each elevator button was last pressed
        elevatorButtonTimes = (abs(time - self.elevatorButtonLastPressed[i]) for i, button in enumerate(elevatorButtons) if button)

        # Get the maximum time, or 1 if no buttons have been pressed
        maxElevatorButtonTime = max(elevatorButtonTimes, default=1)

        targetButtonTime = abs(time - self.elevatorButtonLastPressed[target])

        return 0 if not elevatorButtons[target] else self.elevatorButtonWeight * self.elevatorButtonTimeWeight * (targetButtonTime / max(1, maxElevatorButtonTime))
    
    def _getS3(self, currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, time):
        """
        Get s3, weighted floor button at target
        """
        buttonPressed = floorButtons[target].moveUp or floorButtons[target].moveDown

        return self.floorButtonWeight * buttonPressed
    
    def _getS4(self, currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, time):
        """
        Get s4, weighted time since floor button of target was pressed 
        """
        # Calculate the time since each elevator button was last pressed up
        floorButtonUpTimes = (abs(time - button.lastPressedUp) for button in floorButtons if button.moveUp)

        # Get the maximum time, or 0 if no buttons have been pressed up
        maxFloorButtonUpTime = max(floorButtonUpTimes, default=1)

        # Calculate the time since each elevator button was last pressed down
        floorButtonDownTimes = (abs(time - button.lastPressedDown) for button in floorButtons if button.moveDown)

        # Get the maximum time, or 0 if no buttons have been pressed down
        maxFloorButtonDownTime = max(floorButtonDownTimes, default=1)


        # Get the target button
        targetButton = floorButtons[target]

        # Calculate the time since the button was last pressed up, or 0 if it hasn't been pressed up
        timeSinceLastUp = abs(time - targetButton.lastPressedUp) if targetButton.moveUp else 0

        # Calculate the time since the button was last pressed down, or 0 if it hasn't been pressed down
        timeSinceLastDown = abs(time - targetButton.lastPressedDown) if targetButton.moveDown else 0

        # Calculate the maximum of the two times
        maxTargetFloorButtonTime = max(timeSinceLastUp, timeSinceLastDown)

        return self.floorButtonWeight * self.floorButtonTimeWeight * (maxTargetFloorButtonTime / max(maxFloorButtonUpTime, maxFloorButtonDownTime, 1))
    

    def _getS5(self, currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, time):
        """
        Get s5, weighted amount of elevators moving in targetDirection (in the view of target)
        """
        # Calculate the distance from each elevator to the current floor, excluding the current elevator
        elevatorDistances = [len(elevatorButtons) - abs(e.target - target) for e in elevators if e != elevator]

        return sum(elevatorDistances) * self.competitorWeight
    

    def _getS6(self, currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, time):
        """
        Get s6, weighted distance to target
        """
        return abs(currentFloor - target) * self.distanceWeight ** (self.distanceExponent)