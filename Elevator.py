from Policy import Action
from EventListener import EventListener



class Elevator:
    def __init__(self, minFloor, maxFloor, policy):
        self.passengerEnteredElevatorListener = EventListener() 
        self.passengerExitedElevatorListener = EventListener() 

        self.maxFloor = maxFloor
        self.minFloor = minFloor
        self.currentHeight = 0
        self.fps = 10  # floors per second (in Percent)
        self.decision = Action.Wait
        self.passengerList = []
        self.policy = policy
        self.buttonsPressed = []

    def getCurrentFloor(self):
        return self.currentHeight // 100


    def step(self, building):
        # Check if we are at a floor, approximate if error occurred
        if ((self.currentHeight + self.fps/2) % 100 <= self.fps):
            self.currentHeight = round(self.currentHeight / 100.0) * 100
            self.decision = Action.Wait


        if(self.decision == Action.MoveDown):
            self.currentHeight -= self.fps
        elif(self.decision == Action.MoveUp):
            self.currentHeight += self.fps
        elif(self.decision == Action.Wait):
            self.decision = self.policy.getAction(building.floors, self.buttonsPressed)

        else:
            currentFloor = self.getCurrentFloor()
            for p in self.passengerList:
                if(p.targetFloor == currentFloor):
                    # Call remove
                    self.passengerList.remove(p)
                    passengerExitedElevatorListener.notify_all(p)
                    return
            self.buttonsPressed[currentFloor] = False
                
            floor = building.floors[currentFloor]
            for p in floor.passengerList:
                # Call add
                if((p.targetFloor < currentFloor and self.decision == Action.WaitDown) or
                   (p.targetFloor > currentFloor and self.decision == Action.WaitUp)):
                    floor.passengerList.remove(p)
                    self.passengerList.append(p)
                    self.buttonsPressed[p.target] = True
                    
                    if(self.decision == Action.WaitDown):
                        floor.buttonPressed.moveDown = False
                    else:
                        floor.buttonPressed.moveUp = False
                    passengerEnteredElevatorListener.notify_all(p)
                    return
                
            self.decision = self.policy.getAction(building.floors, self.buttonsPressed)




