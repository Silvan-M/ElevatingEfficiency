from debug import Debug as DB

import random
import numpy as np
from enum import Enum


class FloorDistribution():
    """
    A distribution of how many passengers per floor at a fixed time point.
    """

    def __init__(self, distribution: list):
        self.distribution = distribution

    def __str__(self) -> str:
        return DB.str(
            "Class",
            "Distribution",
            kwargs=[
                self.distribution],
            desc=["distribution"])

    def update_distribution(self, distribution):
        self.distribution = distribution

    def is_chosen(self, index):
        out = self.get_random_index(index) > random.random()
        if (DB.dsrFctIsChosen):
            DB.pr(
                "Func",
                "is_chosen",
                message="function called",
                kwargs=[out],
                desc=["return value"])
        return out

    def get_index_prob(self, index):
        out = self.distribution[index]
        if (DB.dsrFctget_index_prob):
            DB.pr(
                "Func",
                "get_index_prob",
                message="function called",
                kwargs=[out],
                desc=["return value"])
        return out

    def get_random_index(self, exclude=None):
        indices = [i for i, _ in enumerate(self.distribution) if i != exclude]
        weights = [self.distribution[i] for i in indices]
        index = random.choices(indices, weights=weights, k=1)[0]
        if (DB.dsr_fct_random_index):
            DB.pr(
                "Func",
                "get_random_index",
                message="function called",
                kwargs=[index],
                desc=["return value"])
        return index


class EqualFloorDistribution(FloorDistribution):
    """
    A distribution with equal probability for every floor.
    """

    def __init__(self, amount_floors: int):
        self.distribution = []
        for _ in range(amount_floors):
            self.distribution.append(1.0 / amount_floors)


class PeakFloorDistribution(FloorDistribution):
    """
    A distribution with a peak probability for a specific floor.
    """

    def __init__(self, amount_floors: int, peak_floor: int, multiplier: int):
        self.distribution = []
        for _ in range(amount_floors):
            self.distribution.append(1.0 / amount_floors)
        self.distribution[peak_floor] = self.distribution[peak_floor] * multiplier


class TimeDistribution:
    """
    A probability distribution of how many passengers spawn on a floor over time.
    """

    def __init__(self, time_type, max_time_typed, data):
        self.data = []
        self.probabilities = None
        self.lookup_table = None
        self.max_time = max_time_typed
        new_data = []

        for (time, probability) in data:
            if time_type == "m":
                time = time * 60
                self.max_time = max_time_typed * 60
            elif time_type == "h":
                time = time * 60 * 60
                self.max_time = max_time_typed * 60 * 60
            new_data.append((time, probability))

        # Initialize lookup table with zeros
        self.lookup_table = [0] * self.max_time

        self.add_data(new_data)

    def add_data(self, data):
        self.data.extend(data)
        times, people = zip(*self.data)
        self.probabilities = people
        self.max_timePoint = max(times)
        self.precompute_interpolated_probs()

    def precompute_interpolated_probs(self):
        times, _ = zip(*self.data)
        for time in range(0, self.max_time):
            self.lookup_table[time] = np.interp(
                time, times, self.probabilities)

    def get_interpolated_prob(self, time):
        out = self.lookup_table[time % self.max_time]
        if (DB.tdsr_fct_interpolated_prob):
            DB.pr(
                "Func",
                "get_interpolated_prob",
                message="function called",
                kwargs=[out],
                desc=["return value"])
        return out


class TimeSpaceDistribution():
    """
    A distribution of how many passengers spawn on every floor over time.
    max_passengers: The maximum amount of passengers that can spawn in the entire building once.
    time_type: The type of the time values. Can be "s", "m" or "h".
    data: A list of tuples (time, spawnDistribution, target_distribution) with the last two parameters being a Distribution object.
    passenger_distribution: A TimeDistribution object that determines how many passengers spawn in the building at a given time.

    Note: The spawnDistribution and target_distribution of the data parameter contain the probabilities of which floor should be chosen for spawning or as a target.
    """

    def __init__(
            self,
            max_passengers,
            time_type,
            max_time_typed,
            data,
            passenger_distribution,
            distribution_name="Base distribution"):
        self.floorSpawnDistribution = []
        self.floorTargetDistribution = []
        self.passenger_distribution = passenger_distribution
        self.times = []
        self.probabilities = None
        self.max_passengers = max_passengers
        self.max_time_typed = max_time_typed
        self.floor_amount = 0
        self.distribution_name = distribution_name

        if time_type == "m":
            self.max_time = max_time_typed * 60
        elif time_type == "h":
            self.max_time = max_time_typed * 60 * 60
        else:
            self.max_time = max_time_typed

        if time_type == "m":
            self.max_time = max_time_typed * 60
        elif time_type == "h":
            self.max_time = max_time_typed * 60 * 60
        else:
            self.max_time = max_time_typed

        # Create reusable empty floor distributions (to save memory)
        self.distribution_1 = FloorDistribution([])
        self.distribution_2 = FloorDistribution([])

        # Raise Exception if the data is null
        if data is None:
            raise Exception("Data cannot be null.")

        # Sort the data by time, set max_time and floor_amount
        data.sort(key=lambda x: x[0])
        self.floor_amount = len(data[0][1].distribution)

        # Check if every distribution has the same amount of floors
        for (_, spawnDistribution, passenger_distribution) in data:
            if len(
                    spawnDistribution.distribution) != len(
                    passenger_distribution.distribution) or len(
                    spawnDistribution.distribution) != self.floor_amount:
                raise Exception(
                    "Every distribution needs to have the same amount of floors.")

        # Create time distributions for every floor
        for i in range(self.floor_amount):
            floorSpawnTuples = [
                (tupel[0], tupel[1].distribution[i]) for tupel in data]
            floorTargetTuples = [
                (tupel[0], tupel[2].distribution[i]) for tupel in data]

            self.floorSpawnDistribution.append(TimeDistribution(
                time_type, max_time_typed, floorSpawnTuples))
            self.floorTargetDistribution.append(TimeDistribution(
                time_type, max_time_typed, floorTargetTuples))

    def get_passengers_to_spawn(self, time):
        """
        Returns a list of tuples (spawnFloor, target_floor) of the passengers that spawn at the given time.
        """
        floorSpawnDistribution, floorTargetDistribution = self.get_floor_distributions(
            time)

        # Get the amount of passengers that spawn at the given time
        amount = self.get_spawn_amount(time)

        # Get the spawn and target floor for every passenger
        spawn_passengers = []

        for _ in range(amount):
            # Get the spawn and target floor
            spawnFloor = floorSpawnDistribution.get_random_index()

            # Get the target floor, exclude the spawn floor
            target_floor = floorTargetDistribution.get_random_index(spawnFloor)

            spawn_passengers.append((spawnFloor, target_floor))

        return spawn_passengers

    def get_floor_distributions(self, time):
        """
        Returns a list of tuples (spawnDistribution, target_distribution) of the passengers that spawn at the given time.
        """
        # Get the probabilities of the floor distributions, use reusable to
        # save memory
        self.distribution_1.update_distribution(
            [floor.get_interpolated_prob(time) for floor in self.floorSpawnDistribution])
        self.distribution_2.update_distribution(
            [floor.get_interpolated_prob(time) for floor in self.floorTargetDistribution])

        return self.distribution_1, self.distribution_2

    def get_passenger_amount(self, time):
        """
        Returns a double amount of the passengers that spawn at the given time.
        """
        return self.passenger_distribution.get_interpolated_prob(
            time) * self.max_passengers

    def get_spawn_amount(self, time):
        """
        Returns an integer amount of passengers that spawn at the given time using the exponential distribution.
        """
        # Get the interpolated probability of the time distribution
        amount_of_passengers = self.get_passenger_amount(time)

        # Use the exponential distribution to get the amount of passengers that
        # spawn (for max_passengers < 1)
        random_value = round(np.random.exponential(scale=amount_of_passengers))
        return random_value
