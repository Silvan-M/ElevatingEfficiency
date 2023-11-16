from Elevator import Elevator
from Floor import Floor
from Passenger import Passenger

class Building():

    def __init__(self, elevators, floorAmount, spawnDistribution, targetDistribution, timeDistribution):
        self.elevators = elevators
        self.spawnDistribution = spawnDistribution
        self.targetDistribution = targetDistribution
        self.floorAmount = floorAmount
        self.timeDistribution = timeDistribution
        self.floors = []

        for i in range(floorAmount):
            self.floors.append(Floor(i))

    def step(self, time):
        print(len(self.floors[0].passengerList))
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

        self.floors[spawn].spawnPassenger(Passenger(time, spawn, target))
        if(target > spawn):
            self.floors[spawn].buttonPressed.moveUp = True
        else:
            self.floors[spawn].buttonPressed.moveDown = True

    def __str__(self) -> str:
        return "Building with " + str(self.floorAmount) + " floors and " + str(len(self.elevators)) + " elevators."



