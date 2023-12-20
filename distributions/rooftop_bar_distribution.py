from distributions.distribution import TimeSpaceDistribution, TimeDistribution, EqualFloorDistribution, PeakFloorDistribution


class RooftopBarDistribution(TimeSpaceDistribution):
    """
    **Rooftop Bar Scenario**

    Building is open from 08:00 to 24:00, most people come between 20:00 and 22:00, when the rooftop bar is open.
    
    * 00:00 - 07:00: Distributed low usage of building
    * 07:00 - 08:00: Distributed increased usage of building
    * 08:00 - 10:00: Distributed medium usage of building
    * 10:00 - 11:00: Rooftop bar opens, people start coming in from the ground floor (3x more people than other floors)
    * 20:00 - 22:00: Rooftop bar peak usage (20x more people than other floors)
    * 23:00 - 24:00: Rooftop bar closes, people start leaving from the top floor
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
            (11, EqualFloorDistribution(floor_amount), EqualFloorDistribution(floor_amount)),
            (12, PeakFloorDistribution(floor_amount, 0, 3), PeakFloorDistribution(floor_amount, 9, 3)),
            (20, PeakFloorDistribution(floor_amount, 0, 20), PeakFloorDistribution(floor_amount, 9, 20)),
            (22, PeakFloorDistribution(floor_amount, 9, 20), PeakFloorDistribution(floor_amount, 0, 20)),
            (23, PeakFloorDistribution(floor_amount, 9, 3), PeakFloorDistribution(floor_amount, 0, 3)),
            (24, EqualFloorDistribution(floor_amount), EqualFloorDistribution(floor_amount)),
        ]

        # Building is open from 08:00 to 24:00, most people come between 08:00
        # and 24:00, peak at 20:00-22:00
        passenger_distribution = TimeDistribution(
            time_type, max_time_typed, [
                (7, 0.5), (8, 0.6), (20, 1), (22, 1), (23, 0.6), (24, 0.5)])

        # Initialize the TimeSpaceDistribution
        super().__init__(
            max_passengers,
            time_type,
            max_time_typed,
            data,
            passenger_distribution,
            "Rooftop Bar")
