from elevator import Elevator
from floor import Floor
from passenger import Passenger
from delegate import Delegate
from debug import Debug as DB

class Building():

    def __init__(self, elevators, floorAmount, distribution):
        self.onPassengerCreated = Delegate()
        self.elevators = elevators
        self.floorAmount = floorAmount
        self.floors = []
        self.distribution = distribution

        for i in range(floorAmount):
            self.floors.append(Floor(i))

        for i, elevator in enumerate(elevators):
            elevator.setElevatorIndex(i)

    def __str__(self) -> str:
        out = DB.str("Class","Building",kwargs=[self.elevators,self.distribution,self.floorAmount,self.passengerDistribution,self.floors],desc=["elevators","spawn distribution","target distribution","floor amount","time distribution","floors"])
        return out

    def step(self, time):
        if (DB.bldFctStep and ((time % int(DB.bldFctStepsSkip))==0)):
            DB.pr("Func","step",message="function was called")

        # Spawn new passengers
        if (DB.bldFctSpawnPassenger and ((time % int(DB.bldFctSpawnPassengerStepsSkip))==0)):
            DB.pr("Func","spawnPassenger",message="function was called",t=time)

        spawnedPeople = self.distribution.getPassengersToSpawn(time)

        for spawn, target in spawnedPeople:
            self.spawnPassenger(time, spawn, target)

        for elevator in self.elevators:
            elevator.step(time, self)


    def spawnPassenger(self, time, spawn, target):
        # Create passenger object
        passenger = Passenger(time, spawn, target)

        # Notify listeners
        self.onPassengerCreated.notify_all(passenger, time)

        # Add passenger to floor and update floor buttons
        self.floors[spawn].spawnPassenger(passenger, time)

        # Press buttons on floor messages
        if(target > spawn):
            if ((DB.bldPressesFloorButtonUp and ((time % int(DB.bldPressesFloorButtonUpStepsSkip))==0))or (DB.bldPressesFloorButton and ((time % int(DB.bldPressesFloorButtonStepsSkip))==0))):
                DB.pr("Func","spawnPassenger",message="passenger pressed button up",kwargs=[spawn],desc=["floor"],t=time)
        else:
            if ((DB.bldPressesFloorButtonDown and ((time % int(DB.bldPressesFloorButtonDownStepsSkip))==0))or (DB.bldPressesFloorButton and ((time % int(DB.bldPressesFloorButtonStepsSkip))==0))):
                DB.pr("Func","spawnPassenger",message="passenger pressed button down",kwargs=[spawn],desc=["floor"],t=time)






