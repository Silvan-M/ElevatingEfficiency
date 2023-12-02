from policies.policy import Action
from policies.pwdp_policy import PWDPPolicy

class PWDPPolicyEnhanced(PWDPPolicy):
    """
    PWDP Policy Enhanced (Enhanced Parameterized Weighted Decision Policy)
    Similar to PWDP Policy, but this time the elevator knows the direction of the passengers and the amount of passengers
    Policy which gives each pair of (target, targetDestination)
    or in other words (floor, directionTakenAtFloor) a score,
    based on parameters weighing the terms as described below (changes are marked with *):
    * peopleInElevatorButtonWeight: Award high amount of people that pressed elevator button for floor i
    - timeWeight:                   Award high amount of elevator or floor buttons which were pressed a long time ago
    * peopleFloorWeight:            Award high amount of people waiting on floor i
    * directionWeight:              Award high amount of people that pressed floor button [above/below] floor i
    - competitorWeight:             Penalize direction in which other eleavtors are moving
    - distanceWeight:               Penalize high distance to target
    - distanceExponent:             Exponent for distance

    The score for the i-th floor advertising [Up/Down] is calculated as follows (changes are marked with *):
    s1* = peopleInElevatorButtonWeight * amountOfPeopleInElevatorGoingToFloor(i)
    s2  = timeWeight * elevatorButtonPressed[i] * timeSinceElevatorButtonPressed(i) / maxElevatorButtonTime * floorButtons[i].timeSincePressed / maxFloorButtonTime
    s3* = peopleFloorWeight * amountOfPeopleInFloor(i).moving[Up/Down]
    s4* = directionWeight * (amountOfPeople[Above/Below]Target) / (totalAmountOfPeopleInBuilding)
    s5  = competitorWeight * (amountOfElevatorsMoving[Above/Below]) / (totalAmountOfElevators)
    s6  = distanceWeight^(distanceExponent) * abs(currentFloor - i)

    Additionally s3 = 0, s4 = 0, s5 = 0 if elevator capacity is reached

    Then the i-th floor advertising [Up/Down] will have score:
    Score = (s1 + s2 + s3 + s4) / max(1, (s5 + s6))

    Also: The elevator will always follow the direction it advertised
    """

    def __init__(self, peopleInElevatorButtonWeight=1, timeWeight=1, peopleFloorWeight=1, directionWeight=1, competitorWeight=1,  distanceWeight=1, distanceExponent=1):
        self.prevAction = Action.Wait
        self.peopleInElevatorButtonWeight = peopleInElevatorButtonWeight
        self.peopleFloorWeight = peopleFloorWeight

        super().__init__(
            elevatorButtonWeight=1, 
            timeWeight=timeWeight, 
            floorButtonWeight=1, 
            directionWeight=directionWeight, 
            competitorWeight=competitorWeight,  
            distanceWeight=distanceWeight, 
            distanceExponent=distanceExponent
        )

    def name() -> str:
        return  "PWDP Enhanced Policy"
        
    
    # Override functions from PWDPPolicy, rest of the logic remains exactly the same
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

        if (elevator.capacity == len(elevator.passengerList)):
            s3 = 0

        return (s1 + s2 + s3 + s4) / max(1, (s5 + s6))

    def _getS1(self, currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, time):
        """
        Get s1, weighed amount of people in elevator going to target
        """
        # Get amount of people in elevator going to target
        amount = 0
        for p in elevator.passengerList:
            if (p.endLevel == target):
                amount += 1
    
        return self.peopleInElevatorButtonWeight * amount
    
    def _getS3(self, currentFloor, floorButtons, elevator, elevators, elevatorButtons, target, time):
        """
        Get s3, weighed amount of people in floor moving
        """
        amountOfPeopleInFloorMovingInTargetDir = len(self._floorList[target].passengerList)
        
        return self.peopleFloorWeight * amountOfPeopleInFloorMovingInTargetDir
    