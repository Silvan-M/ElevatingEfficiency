from distributions.distribution import TimeSpaceDistribution, TimeDistribution, EqualFloorDistribution, PeakFloorDistribution


class ResidentialBuildingDistribution(TimeSpaceDistribution):
    """
    Residential Building Scenario

    Building constantly has 10x more people entering/exiting than going to other floors.

    People exiting (through floor 0):
    00:00 - 05:00: Low amount of people exiting the building
    05:00 - 06:00: Some people exiting the building (early work)
    06:00 - 10:00: Many people exiting the building (work)
    10:00 - 12:00: Low amount of people exiting the building
    13:00        : Small peak of people exiting the building (lunch)
    14:00 - 24:00: Low amount of people exiting the building

    People entering (through floor 0):
    00:00 - 11:00: Low amount of people entering the building
    12:00        : Small peak of people entering the building (lunch)
    13:00 - 15:00: Low amount of people entering the building
    15:00 - 19:00: Many people entering the building (back from work)
    19:00 - 24:00: Low amount of people entering the building
    """

    def __init__(self):
        time_type = "h"
        max_time_typed = 24

        # Maximum amount of passengers that can spawn in one timestep
        max_passengers = 0.21

        # Amount of floors
        floor_amount = 10

        # Amount of elevators
        self.amount_of_elevators = 2

        # Capacity of elevators
        self.elevator_capacity = 15

        # Set the amount of passengers that spawn on each floor (time [h],
        # spawn distribution, target distribution)
        data = [
            (5, PeakFloorDistribution(floor_amount, 0, 10), PeakFloorDistribution(floor_amount, 0, 10)),
            (6, PeakFloorDistribution(floor_amount, 0, 1 / 10), PeakFloorDistribution(floor_amount, 0, 10)),
            (10, PeakFloorDistribution(floor_amount, 0, 10), PeakFloorDistribution(floor_amount, 0, 10)),
            (11, PeakFloorDistribution(floor_amount, 0, 10), PeakFloorDistribution(floor_amount, 0, 10)),
            (12, PeakFloorDistribution(floor_amount, 0, 10), PeakFloorDistribution(floor_amount, 0, 1 / 10)),
            (13, PeakFloorDistribution(floor_amount, 0, 1 / 10), PeakFloorDistribution(floor_amount, 0, 10)),
            (14, PeakFloorDistribution(floor_amount, 0, 10), PeakFloorDistribution(floor_amount, 0, 10)),
            (15, PeakFloorDistribution(floor_amount, 0, 10), PeakFloorDistribution(floor_amount, 0, 10)),
            (19, PeakFloorDistribution(floor_amount, 0, 10), PeakFloorDistribution(floor_amount, 0, 1 / 10)),
            (20, PeakFloorDistribution(floor_amount, 0, 10), PeakFloorDistribution(floor_amount, 0, 10))
        ]

        # Building is open from 08:00 to 24:00
        passenger_distribution = TimeDistribution(time_type, max_time_typed, [(5, 0.4), (6, 1), (
            10, 0.6), (11, 0.6), (12, 0.8), (13, 0.8), (14, 0.6), (15, 0.6), (19, 1), (20, 0.4), (24, 0.4)])

        # Initialize the TimeSpaceDistribution
        super().__init__(
            max_passengers,
            time_type,
            max_time_typed,
            data,
            passenger_distribution,
            "Residential Building")
