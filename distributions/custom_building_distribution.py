from distributions.distribution import TimeSpaceDistribution, TimeDistribution, EqualFloorDistribution, PeakFloorDistribution, FloorDistribution


class CustomBuildingDistribution(TimeSpaceDistribution):
    """
    Custom Building Scenario

    Choose your own distirbution and parameters for experiments.
    """

    def __init__(self):
        time_type = "h"
        max_time_typed = 24

        # Maximum amount of passengers that can spawn in one timestep
        max_passengers = 0.23

        # Amount of floors
        floor_amount = 10

        # Amount of elevators
        self.amount_of_elevators = 2

        # Capacity of elevators
        self.elevator_capacity = 15

        # Set the amount of passengers that spawn on each floor equally (time
        # [h], spawn distribution, target distribution)
        data = [
            (0, FloorDistribution([0] * 7 +[1] * 3), FloorDistribution([1] * 3 + [0] * 7))]

        # Shopping mall is open from 08:00 to 21:00, most people come between
        # 10:00 and 18:00, peak at 12:00
        passenger_distribution = TimeDistribution(
            time_type, max_time_typed, [(1, 1)])

        super().__init__(
            max_passengers,
            time_type,
            max_time_typed,
            data,
            passenger_distribution,
            "Custom Distribution")
