from Policy import Action
from EventListener import EventListener
from Debug import Debug as DB

import random


class Elevator:
    def __init__(self, minFloor, maxFloor, policy):
        self.passengerEnteredElevatorListener = EventListener() 
        self.passengerExitedElevatorListener = EventListener() 

        self.maxFloor = maxFloor
        self.minFloor = minFloor
        self.currentHeight = random.randint(minFloor*100, (maxFloor-1)*100)
        self.fps = 10  # floors per second (in Percent)
        self.decision = Action.Wait
        self.passengerList = []
        self.policy = policy
        self.buttonsPressed = [False] * (maxFloor+1)
    def __str__(self) -> str:
        return DB.str("Class","Elevator",kwargs=[self.maxFloor,self.minFloor,self.currentHeight,self.fps,self.decision,self.passengerList,self.policy,self.buttonsPressed],\
                                           desc=["max floor","min floor"," current height","fps","decision","passengerlist","policy","buttons pressed"])

    def getCurrentFloor(self):
        return self.currentHeight // 100


    def step(self, time, building):
        if (DB.elvFctStep and ((time % int(DB.elvFctStepsSkips))==0)):
            DB.pr("Func","step",message="function was called",t=time)
        # Check if we are at a floor, approximate if error occurred
        if (((self.currentHeight + self.fps/2) % 100 <= self.fps) and 
            (self.decision == Action.MoveUp or self.decision == Action.MoveDown)):
            self.currentHeight = round(self.currentHeight / 100.0) * 100
            self.decision = Action.Wait

        currentFloor = self.getCurrentFloor()

        if(self.decision == Action.Wait):
            result = self.policy.getAction(currentFloor, building.floors, self.buttonsPressed)
            self.decision = result
        elif (self.decision == Action.WaitUp or self.decision == Action.WaitDown):
            for p in self.passengerList:
                if(p.endLevel == currentFloor):
                    # Call remove
                    if (DB.elvPassengerLeavesElevator and ((time % int(DB.elvPassengerLeavesElevatorSkips))==0)):
                        DB.pr("Func","step",message="passenger left elevator",t=time,kwargs=[p],desc=["passenger"])
                    self.passengerList.remove(p)
                    self.passengerExitedElevatorListener.notify_all(p, time)
                    return
            self.buttonsPressed[currentFloor] = False
            
            floor = building.floors[currentFloor]
            for p in floor.passengerList:
                # Call add
                if((p.endLevel < currentFloor and self.decision == Action.WaitDown) or
                   (p.endLevel > currentFloor and self.decision == Action.WaitUp)):
                    floor.passengerList.remove(p)
                    if (DB.elvPassengerEntersElevator and ((time % int(DB.elvPassengerEntersElevatorSkips))==0) ):
                        DB.pr("Func","step",message="passenger entered elevator",t=time,kwargs=[p],desc=["passenger"])
                    self.passengerList.append(p)
                    self.buttonsPressed[p.endLevel] = True
                    if (DB.elvPassengerPressedButton and ((time % int(DB.elvPassengerPressedButtonSkips))==0) ):
                        DB.pr("Func","step",message="passenger pressed button",t=time,kwargs=[p.endLevel],desc=["level"])
                    
                    if(self.decision == Action.WaitDown):
                        floor.buttonPressed.moveDown = False
                    else:
                        floor.buttonPressed.moveUp = False

                    self.passengerEnteredElevatorListener.notify_all(p, time)
                    return
                
            self.decision = self.policy.getAction(currentFloor, building.floors, self.buttonsPressed)
            if (DB.elvDecisionUpdate and ((time % int(DB.elvDecisionUpdateSkips))==0) ):
                DB.pr("Func","step",message="decision was updated",t=time,kwargs=[self.decision],desc=["decision"])
                  
        # Finally move
        if(self.decision == Action.MoveDown):
            self.currentHeight = max(0, self.currentHeight - self.fps)
        elif(self.decision == Action.MoveUp):
            self.currentHeight = min((self.maxFloor-1)*100, self.currentHeight + self.fps)
        if (DB.elvMovementUpdate and ((time % int(DB.elvMovementUpdateSkips))==0) ):
            DB.pr("Func","step",message="elevator moved",t=time,kwargs=[self.currentHeight],desc=["height"])




