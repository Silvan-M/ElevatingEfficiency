from Elevator import Elevator
from Floor import Floor
from Passenger import Passenger
from EventListener import EventListener

class Building():

    def __init__(self, elevators, floorAmount, spawnDistribution, targetDistribution, timeDistribution):
        self.passengerCreatedListener = EventListener()
        self.elevators = elevators
        self.spawnDistribution = spawnDistribution
        self.targetDistribution = targetDistribution
        self.floorAmount = floorAmount
        self.timeDistribution = timeDistribution
        self.floors = []

        for i in range(floorAmount):
            self.floors.append(Floor(i))

    def step(self, time):
        # Spawn new passengers
        spawnedPeople = 10
        for i in range(spawnedPeople):
            self.spawnPassenger(time)

        for elevator in self.elevators:
            elevator.step(self)


    def spawnPassenger(self, time):
        spawn = self.spawnDistribution.getRandomIndex(self)
        target = spawn
        while target == spawn:
            target = self.targetDistribution.getRandomIndex(self)

        passenger = Passenger(time, spawn, target)
        self.floors[spawn].spawnPassenger(passenger)
        if(target > spawn):
            self.floors[spawn].buttonPressed.moveUp = True
        else:
            self.floors[spawn].buttonPressed.moveDown = True

        self.passengerCreatedListener.notify_all(passenger, time)

    def __str__(self) -> str:
        return "Building with " + str(self.floorAmount) + " floors and " + str(len(self.elevators)) + " elevators."



