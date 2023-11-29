from distributions.distribution import TimeSpaceDistribution, TimeDistribution, EqualFloorDistribution

class ShoppingMallDistribution(TimeSpaceDistribution):
    """
    Shopping Mall Scenario
    
    Shopping mall is open from 08:00 to 21:00, most people come between 10:00 and 18:00, peak at 12:00
    00:00 - 08:00: Distributed low usage of building
    08:00 - 10:00: Distributed usage of building going up
    10:00 - 12:00: Distributed usage gradient to peak
    12:00 - 18:00: Distributed usage gradient to normal
    18:00 - 24:00: Distributed usage of building going down
    """
    def __init__(self):
        timeType = "h"

        # Maximum amount of passengers that can spawn in one timestep
        maxPassengers = 0.4

        # Amount of floors
        floorAmount = 10

        # Amount of elevators
        self.amountOfElevators = 4

        # Capacity of elevators
        self.elevatorCapacity = 10

        # Set the amount of passengers that spawn on each floor equally (time [h], spawn distribution, target distribution)
        data = [
            (0, EqualFloorDistribution(floorAmount), EqualFloorDistribution(floorAmount)),
            (24, EqualFloorDistribution(floorAmount), EqualFloorDistribution(floorAmount))
        ]

        # Shopping mall is open from 08:00 to 21:00, most people come between 10:00 and 18:00, peak at 12:00
        timeDistribution = TimeDistribution(timeType, [(8, 0.3), (10, 0.8), (12, 1), (18, 0.8), (24, 0.3)])

        # Initialize the TimeSpaceDistribution
        super().__init__(maxPassengers, timeType, data, timeDistribution)