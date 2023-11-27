from elevator import Elevator
from floor import Floor
from passenger import Passenger
from delegate import Delegate
from debug import Debug as DB

class Building():

    def __init__(self, elevators, floorAmount, spawnDistribution, targetDistribution, timeDistribution):
        self.onPassengerCreated = Delegate()
        self.elevators = elevators
        self.spawnDistribution = spawnDistribution
        self.targetDistribution = targetDistribution
        self.floorAmount = floorAmount
        self.timeDistribution = timeDistribution
        self.floors = []

        for i in range(floorAmount):
            self.floors.append(Floor(i))

        for i, elevator in enumerate(elevators):
            elevator.setElevatorIndex(i)

    def __str__(self) -> str:
        out = DB.str("Class","Building",kwargs=[self.elevators,self.spawnDistribution,self.targetDistribution,self.floorAmount,self.timeDistribution,self.floors],desc=["elevators","spawn distribution","target distribution","floor amount","time distribution","floors"])
        return out

    def step(self, time):
        if (DB.bldFctStep and ((time % int(DB.bldFctStepsSkip))==0)):
            DB.pr("Func","step",message="function was called")

        # Spawn new passengers
        spawnedPeople = round(self.timeDistribution.getRandomProb(time))
        if (DB.bldFctSpawnPassenger and ((time % int(DB.bldFctSpawnPassengerStepsSkip))==0)):
            DB.pr("Func","spawnPassenger",message="function was called",t=time)
        for i in range(spawnedPeople):
            self.spawnPassenger(time)

        for elevator in self.elevators:
            elevator.step(time, self)


    def spawnPassenger(self, time):

        spawn = self.spawnDistribution.getRandomIndex(self)
        target = spawn
        while target == spawn:
            target = self.targetDistribution.getRandomIndex(self)

        passenger = Passenger(time, spawn, target)
        self.onPassengerCreated.notify_all(passenger, time)
        self.floors[spawn].spawnPassenger(passenger)
        if(target > spawn):
            self.floors[spawn].buttonPressed.setMoveUp(True, time)
            if ((DB.bldPressesFloorButtonUp and ((time % int(DB.bldPressesFloorButtonUpStepsSkip))==0))or (DB.bldPressesFloorButton and ((time % int(DB.bldPressesFloorButtonStepsSkip))==0))):
                DB.pr("Func","spawnPassenger",message="passenger pressed button up",kwargs=[spawn],desc=["floor"],t=time)
        else:
            self.floors[spawn].buttonPressed.setMoveDown(True, time)
            if ((DB.bldPressesFloorButtonDown and ((time % int(DB.bldPressesFloorButtonDownStepsSkip))==0))or (DB.bldPressesFloorButton and ((time % int(DB.bldPressesFloorButtonStepsSkip))==0))):
                DB.pr("Func","spawnPassenger",message="passenger pressed button down",kwargs=[spawn],desc=["floor"],t=time)






