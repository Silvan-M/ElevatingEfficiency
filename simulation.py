from simulation_statistics import SimulationStatistics
from delegate import Delegate
from debug import Debug as DB

import time
import numpy as np
import random


class Simulation():

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
        self.time = self._convert_time(days, hours, minutes, seconds)

    def run(self, days=0, hours=0, minutes=0, seconds=0, time_scale=-1):
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
