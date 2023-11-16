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
        self.buttonsPressed = [False] * (maxFloor+1)

    def getCurrentFloor(self):
        return self.currentHeight // 100


    def step(self, time, building):
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
                    self.passengerList.append(p)
                    self.buttonsPressed[p.endLevel] = True
                    
                    if(self.decision == Action.WaitDown):
                        floor.buttonPressed.moveDown = False
                    else:
                        floor.buttonPressed.moveUp = False

                    self.passengerEnteredElevatorListener.notify_all(p, time)
                    return
                
            self.decision = self.policy.getAction(currentFloor, building.floors, self.buttonsPressed)

        # Finally move
        if(self.decision == Action.MoveDown):
            self.currentHeight = max(0, self.currentHeight - self.fps)
        elif(self.decision == Action.MoveUp):
            self.currentHeight = min(self.maxFloor*100, self.currentHeight + self.fps)




