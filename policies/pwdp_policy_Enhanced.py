from policies.policy import Action
from policies.pwdp_policy import PWDPPolicy

class PWDPPolicyEnhanced(PWDPPolicy):
    """
    PWDP Policy Enhanced (Enhanced Parameterized Weighted Decision Policy)
    Similar to PWDP Policy, but this time the elevator knows the direction of the passengers and the amount of passengers
    Policy which gives each pair of (target, targetDestination)
    or in other words (floor, directionTakenAtFloor) a score,
    based on parameters weighing the terms as described below (changes are marked with *):
    * peopleInElevatorButtonWeight: Amount of people, which pressed the elevator button to floor i
    * peopleFloorWeight:            Amount of people waiting on floor
    * directionWeight:              Weight of amount of people waiting above or below
    - distanceWeight:               Distance to target
    - distanceExponent:             Exponent for distance
    - timeWeight:                   Time since button was pressed

    The score for the i-th floor advertising [Up/Down] is calculated as follows (changes are marked with *):
    A* = peopleInElevatorButtonWeight * amountOfPeopleInElevatorGoingToFloor(i)
    B  = timeWeight * timeSinceElevatorButtonPressed(i) / maxElevatorButtonTime
    C* = peopleFloorWeight * amountOfPeopleInFloor(i).moving[Up/Down]
    D* = directionWeight * (amountOfPeople[Above/Below]Target) / (totalAmountOfPeopleInBuilding)
    E  = distanceWeight^(distanceExponent) * abs(currentFloor - i)

    Then the i-th floor advertising [Up/Down] will have score:
    Score = (A + B + D + C) / E

    Also: The elevator will always follow the direction it advertised
    """

    def __init__(self, peopleInElevatorButtonWeight=1, peopleFloorWeight=1, directionWeight=1, distanceWeight=1, distanceExponent=1, timeWeight=1):
        self.prevAction = Action.Wait
        self.peopleInElevatorButtonWeight = peopleInElevatorButtonWeight
        self.peopleFloorWeight = peopleFloorWeight
        
        super().__init__(elevatorButtonWeight=1, 
                         floorButtonWeight=1, 
                         directionWeight=directionWeight, 
                         distanceWeight=distanceWeight, 
                         distanceExponent=distanceExponent, 
                         timeWeight=timeWeight)

    def _amountOfPeopleInElevatorGoingToFloor(self, target, elevator):
        """
        Get amount of people in elevator going to target
        """
        amount = 0
        for p in elevator.passengerList:
            if (p.endLevel == target):
                amount += 1
        return amount
    
    def _getAmountOfPeopleInTargetDirectionNormalized(self, currentFloor, target, targetDirection):
        """
        Get amount of people in target direction in normalized form (divided by total amount of people in building)
        """
        amount = 0
        totalAmount = 0

        for target in range(len(self._floorList)):
            totalAmount += len(self._floorList[target].passengerList)
            if (targetDirection == 1 and target <= currentFloor):
                continue
            elif (targetDirection == -1 and target >= currentFloor):
                continue
            elif (target == currentFloor):
                continue
            
            amount += len(self._floorList[target].passengerList)

        return amount / totalAmount

    def _getScore(self, currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, targetDirection, time):
        """
        Get score for target and targetDirection
        """
        maxElevatorButtonTime = time - self.minElevatorButtonTime if (self.minElevatorButtonTime != 0) else 1

        amountOfPeopleInFloorMovingInTargetDir = 0
        for p in self._floorList[target].passengerList:
            if (p.endLevel > target and targetDirection == Action.MoveUp) or \
               (p.endLevel < target and targetDirection == Action.MoveDown):
                amountOfPeopleInFloor += 1

        
        A = self.peopleInElevatorButtonWeight * self._amountOfPeopleInElevatorGoingToFloor(target, elevator)
        B = self.timeWeight * self._timeSinceElevatorButtonPressed(target, time) / maxElevatorButtonTime
        C = self.peopleFloorWeight * amountOfPeopleInFloorMovingInTargetDir
        D = self.directionWeight * self._getAmountOfPeopleInTargetDirectionNormalized(currentFloor, target, targetDirection)
        E = abs(currentFloor - target) * self.distanceWeight ** (self.distanceExponent)
        
        return A + B + D + C - E
    