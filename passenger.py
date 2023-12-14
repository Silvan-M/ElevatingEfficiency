import random
import sys

from debug import Debug as DB


class Passenger():
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
