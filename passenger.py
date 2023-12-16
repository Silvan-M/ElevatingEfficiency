import random
import sys

from debug import Debug as DB


class Passenger():
    """
    Represents a passenger

    :param start_time: The time the passenger was created
    :type start_time: int
    :param start_level: The level the passenger was created on
    :type start_level: int
    :param end_level: The level the passenger wants to go to
    :type end_level: int
    """

    def __init__(self, start_time, start_level, end_level):
        self.id = random.randint(0, sys.maxsize)
        self.start_level = start_level
        self.current_level = start_level
        self.end_level = end_level
        self.start_time = start_time

    def __str__(self) -> str:
        return DB.str(
            "File",
            "Passenger",
            kwargs=[
                self.start_level,
                self.current_level,
                self.end_level,
                self.start_time,
                self.id],
            desc=[
                "starting level",
                "current level",
                "target level",
                "start time",
                "id"])
