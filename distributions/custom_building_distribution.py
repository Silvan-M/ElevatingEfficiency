from distributions.distribution import TimeSpaceDistribution, TimeDistribution, EqualFloorDistribution, PeakFloorDistribution, FloorDistribution

class CustomBuildingDistribution(TimeSpaceDistribution):
    """
    Custom Building Scenario
    
    Choose your own distirbution and parameters for experiments.
    """
    def __init__(self):
        timeType = "h"
        maxTimeTyped = 24

        # Maximum amount of passengers that can spawn in one timestep
        maxPassengers = 0.23

        # Amount of floors
        floorAmount = 10

        # Amount of elevators
        self.amountOfElevators = 2

        # Capacity of elevators
        self.elevatorCapacity = 15

        # Set the amount of passengers that spawn on each floor equally (time [h], spawn distribution, target distribution)
        data = [
            (0, FloorDistribution([0]*7 + [1]*3), FloorDistribution([1]*3 + [0]*7))
        ]

        # Shopping mall is open from 08:00 to 21:00, most people come between 10:00 and 18:00, peak at 12:00
        timeDistribution = TimeDistribution(timeType, maxTimeTyped, [(1, 1)])

        super().__init__(maxPassengers, timeType, maxTimeTyped, data, timeDistribution, "Custom Distribution")