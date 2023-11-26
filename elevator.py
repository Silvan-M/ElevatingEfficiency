from policies import Action
from delegate import Delegate
from debug import Debug as DB

import random


class Elevator:
    def __init__(self, minFloor, maxFloor, policy, elevatorIndex, capacity):
        self.onPassengerEntered = Delegate() 
        self.onPassengerExited = Delegate() 

        self.maxFloor = maxFloor
        self.minFloor = minFloor
        self.currentHeight = random.randint(minFloor*100, (maxFloor)*100)
        self.fps = 10  # floors per second (in Percent)
        self.decision = Action.Wait
        self.passengerList = []
        self.policy = policy
        self.elevatorButtons = [False] * (maxFloor+1)
        self.elevatorIndex = elevatorIndex
        self.target = -1            # Target floor
        self.targetDirection = 0    # Direction that will be taken once reached target (-1 = down, 0 = undefined, 1 = up)
        self.capacity = capacity
    
    def __str__(self) -> str:
        return DB.str("Class","Elevator",kwargs=[self.maxFloor,self.minFloor,self.currentHeight,self.fps,self.decision,self.passengerList,self.policy,self.elevatorButtons],\
                                           desc=["max floor","min floor"," current height","fps","decision","passengerlist","policy","buttons pressed"])

    def getCurrentFloor(self):
        return self.currentHeight // 100
    def getElevatorIndex(self):
        return self.elevatorIndex

    def step(self, time, building):
        if (DB.elvFctStep and ((time % int(DB.elvFctStepsSkips))==0)):
            DB.pr("Func","step",message="function was called",t=time)

        # Check if we are at a floor, approximate if error occurred
        if (((self.currentHeight + self.fps/2) % 100 <= self.fps) and 
            (self.decision == Action.MoveUp or self.decision == Action.MoveDown)):
            # Wait for policy to make a decision
            self.currentHeight = round(self.currentHeight / 100.0) * 100
            self.decision = Action.Wait

        currentFloor = self.getCurrentFloor()

        if(self.decision == Action.Wait or self.decision == Action.WaitOpen):
            # Waiting, get decision from policy
            self.decision = self.policy.getAction(currentFloor, building.floors, self.elevatorButtons, building.elevators, self, time)
        elif (self.decision == Action.WaitUp or self.decision == Action.WaitDown):
            # Waiting to go up or down, ask passengers to enter if they go in same direction

            # Check if any passenger wants to leave
            for p in self.passengerList:
                if(p.endLevel == currentFloor):
                    if (DB.elvPassengerLeavesElevator and ((time % int(DB.elvPassengerLeavesElevatorSkips))==0)):
                        DB.pr("Func","step",message="passenger left elevator",t=time,kwargs=[p],desc=["passenger"])

                    # Remove passenger from elevator, notify observers (for statistics)
                    self.passengerList.remove(p)
                    self.onPassengerExited.notify_all(p, time)
                    return
                
            # Since we arrived at floor, disable button
            self.elevatorButtons[currentFloor] = False
            
            # Check if any passenger wants to enter
            floor = building.floors[currentFloor]
            for p in floor.passengerList:
                # Check if passenger wants to go in same direction
                if ((p.endLevel < currentFloor and self.decision == Action.WaitDown) or
                   (p.endLevel > currentFloor and self.decision == Action.WaitUp) and self.capacity > len(self.passengerList)):
                    # Elevator still has capacity and a passenger wants to enter, thus passenger leaves floor
                    floor.passengerList.remove(p)
                    
                    if (DB.elvPassengerEntersElevator and ((time % int(DB.elvPassengerEntersElevatorSkips))==0) ):
                        DB.pr("Func","step",message="passenger entered elevator",t=time,kwargs=[p],desc=["passenger"])

                    # Add passenger to elevator and press button of passenger destination
                    self.passengerList.append(p)
                    self.elevatorButtons[p.endLevel] = True

                    if (DB.elvPassengerPressedButton and ((time % int(DB.elvPassengerPressedButtonSkips))==0) ):
                        DB.pr("Func","step",message="passenger pressed button",t=time,kwargs=[p.endLevel],desc=["level"])
                    
                    # Disable button on floor
                    if(self.decision == Action.WaitDown):
                        floor.buttonPressed.setMoveDown(False, time)
                    else:
                        floor.buttonPressed.setMoveUp(False, time)

                    self.onPassengerEntered.notify_all(p, time)

                    # We let only one passenger enter per step, thus return
                    return

            # Now that we let all passengers enter, get new decision from policy
            self.decision = self.policy.getAction(currentFloor, building.floors, self.elevatorButtons, building.elevators, self, time)
            
            if (DB.elvDecisionUpdate and ((time % int(DB.elvDecisionUpdateSkips))==0) ):
                DB.pr("Func","step",message="decision was updated",t=time,kwargs=[self.decision],desc=["decision"])
                  
        # Finally move
        if(self.decision == Action.MoveDown):
            self.currentHeight = max(0, self.currentHeight - self.fps)
        elif(self.decision == Action.MoveUp):
            self.currentHeight = min((self.maxFloor)*100, self.currentHeight + self.fps)

        if (DB.elvMovementUpdate and ((time % int(DB.elvMovementUpdateSkips))==0) ):
            DB.pr("Func","step",message="elevator moved",t=time,kwargs=[self.currentHeight],desc=["height"])
        




