from distributions.distribution import TimeSpaceDistribution, TimeDistribution, EqualFloorDistribution, PeakFloorDistribution


class LowDensityDistribution(TimeSpaceDistribution):
    """
    **Low Density Distribution Scenario**

    Equal start and target distribution for the whole day.
    Low amount of passengers
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
            (0, EqualFloorDistribution(floor_amount), EqualFloorDistribution(floor_amount)),
            (24, EqualFloorDistribution(floor_amount), EqualFloorDistribution(floor_amount)),
        ]

        passenger_distribution = TimeDistribution(
            time_type, max_time_typed, [(0, 0.5), (24, 0.5)])

        # Initialize the TimeSpaceDistribution
        super().__init__(
            max_passengers,
            time_type,
            max_time_typed,
            data,
            passenger_distribution,
            "Low Density Distribution")
