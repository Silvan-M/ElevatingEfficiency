from distributions.distribution import TimeSpaceDistribution, TimeDistribution, EqualFloorDistribution, PeakFloorDistribution

class HighDensityDistribution(TimeSpaceDistribution):
    """
    High Density Distribution Scenario

    Equal start and target distribution for the whole day.
    High amount of passengers
    """
    def __init__(self):
        timeType = "h"
        maxTimeTyped = 24

        # Maximum amount of passengers that can spawn in one timestep
        maxPassengers = 0.21

        # Amount of floors
        floorAmount = 10

        # Amount of elevators
        self.amountOfElevators = 2

        # Capacity of elevators
        self.elevatorCapacity = 15

        # Set the amount of passengers that spawn on each floor (time [h], spawn distribution, target distribution)
        data = [
            (0, EqualFloorDistribution(floorAmount), EqualFloorDistribution(floorAmount)),
            (24, EqualFloorDistribution(floorAmount), EqualFloorDistribution(floorAmount)),
        ]

        timeDistribution = TimeDistribution(timeType, maxTimeTyped, [(0, 1), (24, 1)])

        # Initialize the TimeSpaceDistribution
        super().__init__(maxPassengers, timeType, maxTimeTyped, data, timeDistribution, "High Density Distribution")