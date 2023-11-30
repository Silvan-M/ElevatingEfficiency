from distributions.distribution import TimeSpaceDistribution, TimeDistribution, EqualFloorDistribution, PeakFloorDistribution

class CustomBuildingDistribution(TimeSpaceDistribution):
    """
    Custom Building Scenario
    
    Choose your own distirbution and parameters for experiments.
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

        # Set the amount of passengers that spawn on each floor (time [timeType], spawn distribution, target distribution)
        data = [
            (6, EqualFloorDistribution(floorAmount), EqualFloorDistribution(floorAmount)),
            (12, PeakFloorDistribution(floorAmount, 0, 10), PeakFloorDistribution(floorAmount, 0, 10)),
            (22, EqualFloorDistribution(floorAmount), EqualFloorDistribution(floorAmount)),
        ]
        
        # When spawn how many people [0,1] 
        timeDistribution = TimeDistribution(timeType, maxTimeTyped, [(5, 0.4), (6, 1), (10, 0.6), (11, 0.6), (12, 0.8), (13, 0.8), (14, 0.6), (15, 0.6), (19, 1), (20, 0.4)])

        # Initialize the TimeSpaceDistribution
        super().__init__(maxPassengers, timeType, maxTimeTyped, data, timeDistribution)