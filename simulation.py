from simulation_statistics import SimulationStatistics
from delegate import Delegate
from debug import Debug as DB

import time
import numpy as np
import random


class Simulation():
    """
    Simulates the building and the elevators

    :param building: The building to simulate
    :type building: Building
    :param seed: The seed to use for the random number generator
    :type seed: int
    """

    def __init__(self, building, seed=-1):
        self.time = 0
        self.on_simulation_started = Delegate()
        self.on_step_end = Delegate()
        self.on_simulation_finished = Delegate()
        self.building = building
        self.statistics = SimulationStatistics(self)
        self.seed = seed

    def __str__(self, level=0) -> str:
        out = DB.str(
            "Class", "Simulation", kwargs=[
                self.time, self.building], desc=[
                "time", "building"])
        return out

    def _convert_time(self, days=0, hours=0, minutes=0, seconds=0):
        return (days * 24 * 60 * 60
                + hours * 60 * 60 +
                + minutes * 60
                + seconds)

    def set_time(self, days=0, hours=0, minutes=0, seconds=0):
        """
        Sets the time of the simulation

        :param days: The amount of days to set the time to
        :type days: int
        :param hours: The amount of hours to set the time to
        :type hours: int
        :param minutes: The amount of minutes to set the time to
        :type minutes: int
        :param seconds: The amount of seconds to set the time to
        :type seconds: int
        """
        self.time = self._convert_time(days, hours, minutes, seconds)

    def run(self, days=0, hours=0, minutes=0, seconds=0, time_scale=-1):
        """
        Starts the simulation

        :param days: The amount of days to run the simulation for
        :type days: int
        :param hours: The amount of hours to run the simulation for
        :type hours: int
        :param minutes: The amount of minutes to run the simulation for
        :type minutes: int
        :param seconds: The amount of seconds to run the simulation for
        :type seconds: int
        :param time_scale: Set the speed of the simulation, only for visualisation purposes, -1 for no delay 
        :type time_scale: float
        """
        if (self.seed != -1):
            random.seed(self.seed)
            np.random.seed(self.seed)

        step_amount = self._convert_time(days, hours, minutes, seconds)

        self.on_simulation_started.notify_all(self, self.time, step_amount)
        for i in range(step_amount):
            self.step()

            if (time_scale > 0):
                time.sleep(time_scale)

        self.on_simulation_finished.notify_all(self)

    def step(self):
        """
        Steps the simulation one time step forward
        """
        if (DB.sim_fct_step and ((self.time % int(DB.sim_time_steps_skip)) == 0)):
            DB.pr("Func", "step", message="function was called", t=self.time)

        self.building.step(self.time)
        self.time += 1

        self.on_step_end.notify_all(self, self.time)
        if (DB.sim_time_steps and ((self.time % int(DB.sim_fct_stepSkip)) == 0)):
            DB.pr(
                "Func",
                "step",
                kwargs=[
                    self.time],
                desc=["time incremented to "],
                t=self.time)
