from distributions.distribution import TimeSpaceDistribution, TimeDistribution, EqualFloorDistribution

class ShoppingMallDistribution(TimeSpaceDistribution):
    def __init__(self):
        timeType = "h"

        # Maximum amount of passengers that can spawn in one timestep
        self.maxPassengers = 0.2

        # Amount of floors
        self.floorAmount = 5

        # Amount of elevators
        self.amountOfElevators = 1

        # Capacity of elevators
        self.elevatorCapacity = 10

        # Set the amount of passengers that spawn on each floor equally (time [h], spawn distribution, target distribution)
        data = [
            (0, EqualFloorDistribution(10), EqualFloorDistribution(10)),
            (24, EqualFloorDistribution(10), EqualFloorDistribution(10))
        ]

        # Shopping mall is open from 08:00 to 21:00, most people come between 10:00 and 18:00, peak at 12:00
        timeDistribution = TimeDistribution(timeType, [(8, 0), (10, 0.8), (12, 1), (18, 0.8), (24, 0)])
        super().__init__(self.maxPassengers, timeType, data, timeDistribution)