from distributions.distribution import TimeSpaceDistribution, TimeDistribution, EqualFloorDistribution, PeakFloorDistribution

class RooftopBarDistribution(TimeSpaceDistribution):
    """
    Rooftop Bar Scenario

    Building is open from 08:00 to 24:00, most people come between 20:00 and 22:00, when the rooftop bar is open.
    00:00 - 07:00: Distributed low usage of building
    07:00 - 08:00: Distributed increased usage of building
    08:00 - 10:00: Distributed medium usage of building
    10:00 - 11:00: Rooftop bar opens, people start coming in from the ground floor (3x more people than other floors)
    20:00 - 22:00: Rooftop bar peak usage (20x more people than other floors)
    23:00 - 24:00: Rooftop bar closes, people start leaving from the top floor
    """
    def __init__(self):
        timeType = "h"

        # Maximum amount of passengers that can spawn in one timestep
        maxPassengers = 0.2

        # Amount of floors
        floorAmount = 20

        # Amount of elevators
        self.amountOfElevators = 2

        # Capacity of elevators
        self.elevatorCapacity = 10

        # Set the amount of passengers that spawn on each floor (time [h], spawn distribution, target distribution)
        data = [
            (11, EqualFloorDistribution(floorAmount), EqualFloorDistribution(floorAmount)),
            (12, PeakFloorDistribution(floorAmount, 0, 3), PeakFloorDistribution(floorAmount, 19, 3)),
            (20, PeakFloorDistribution(floorAmount, 0, 20), PeakFloorDistribution(floorAmount, 19, 20)),
            (22, PeakFloorDistribution(floorAmount, 19, 20), PeakFloorDistribution(floorAmount, 0, 20)),
            (23, PeakFloorDistribution(floorAmount, 19, 3), PeakFloorDistribution(floorAmount, 0, 3)),
            (24, EqualFloorDistribution(floorAmount), EqualFloorDistribution(floorAmount)),
        ]

        # Building is open from 08:00 to 24:00, most people come between 08:00 and 24:00, peak at 20:00-22:00
        timeDistribution = TimeDistribution(timeType, [(7, 0.5), (8, 0.6), (20, 1), (22, 1), (23, 0.6), (24, 0.5)])

        # Initialize the TimeSpaceDistribution
        super().__init__(maxPassengers, timeType, data, timeDistribution)