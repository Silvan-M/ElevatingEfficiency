import sys
import matplotlib.pyplot as plt
import csv
import statistics
from itertools import groupby
from operator import attrgetter
from enum import Enum


class Objective(Enum):
    AWT = "average waiting time"  # average waiting time
    AWTSD = "standard deviation of waiting time" # average waiting time's standard deviation
    ATTD = "average time to destination"  # average time to destination
    ACE = "average crowededness"  # average crowdedness in elevator
    AMP = "amount of people"  # amount of people spawned


class SimulationStatistics():
    """
    Tracks necessary information of the simulation for plots.
    """

    def __init__(self, simulation):
        simulation.on_simulation_started.add_listener(
            self.on_simulation_started)
        simulation.on_step_end.add_listener(self.on_step_end)
        self.finished_tasks = {}
        self.crowdedness = []

    def on_simulation_started(self, simulation, start_time, step_amount):
        """
        Initializes a new simulation
        
        :simulation: The simulation object to track
        :start_time: Time in seconds of the time of day
        :step_amount: Time in seconds of the duration
        """

        # Add delegates
        building = simulation.building
        simulation.on_simulation_finished.add_listener(self.on_simulation_finished)
        building.on_passenger_created.add_listener(self.on_passenger_created)
        for e in building.elevators:
            e.on_passenger_entered.add_listener(self.on_passenger_entered)
            e.on_passenger_exited.add_listener(self.on_passenger_exited)

    def on_step_end(self, simulation, time):
        """
        Called once one simulation step finished
        
        :simulation: The simulation object to track
        :time: Current time in seconds
        """
        building = simulation.building
        count = sum(len(e.passenger_list) for e in building.elevators)
        self.crowdedness.append(count / len(building.elevators))

    def on_simulation_finished(self, simulation):
        """
        Called once entire simulation finished
        
        :simulation: The simulation object to track
        """

        time = simulation.time
        # Augment data for those who didn't finish in time
        for t in self.finished_tasks:
            val = self.finished_tasks[t]
            if val.waiting_time < 0:
                val.waiting_time = time - val.start_time
            if val.total_time < 0:
                val.total_time = time - val.start_time

        self.write_to_file("results.txt")

    def on_passenger_created(self, passenger, time):
        """
        Called once one passenger created
        
        :passenger: The passenger object created
        :time: Current time in seconds
        """

        self.finished_tasks[passenger.id] = FinishInfo(
            passenger.id, passenger.start_level, passenger.end_level, passenger.start_time)

    def on_passenger_entered(self, passenger, time):
        """
        Called once one passenger entered the elevator
        
        :passenger: The passenger object created
        :time: Current time in seconds
        """
        self.finished_tasks[passenger.id].waiting_time = time - \
            passenger.start_time

    def on_passenger_exited(self, passenger, time):
        """
        Called once one passenger exited the elevator
        
        :passenger: The passenger object created
        :time: Current time in seconds
        """
        self.finished_tasks[passenger.id].total_time = time - passenger.start_time

    def write_to_file(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'PassengerID',
                'Start',
                'Target',
                'StartTime',
                'WaitingTime',
                'TotalTime']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for task in self.finished_tasks.values():
                writer.writerow({'PassengerID': task.id,
                                 'Start': task.start,
                                 'Target': task.target,
                                 'StartTime': task.start_time,
                                 'WaitingTime': task.waiting_time,
                                 'TotalTime': task.total_time})

    def calculate_average_waiting_time(self, from_time=-1, to_time=sys.maxsize):
        """
        Get the average time the passengers have been waiting for an elevator to arrive
        
        :from_time: start time in seconds
        :to_time: end time in seconds
        """
        waiting_times = [task.waiting_time for task in self.finished_tasks.values(
        ) if task.start_time >= from_time and task.start_time <= to_time]
        return statistics.mean(waiting_times) if waiting_times else None

    def calculate_std_dev_waiting_time(self, from_time=-1, to_time=sys.maxsize):
        """
        Get the standard deviation time the passengers have been waiting for an elevator to arrive
        
        :from_time: start time in seconds
        :to_time: end time in seconds
        """

        waiting_times = [task.waiting_time for task in self.finished_tasks.values(
        ) if task.start_time >= from_time and task.start_time <= to_time]
        return statistics.stdev(waiting_times) if len(
            waiting_times) > 1 else None

    def calculate_amount_people_spawned(self, from_time=-1, to_time=sys.maxsize):
        """
        Get the amount of passengers spawned
        
        :from_time: start time in seconds
        :to_time: end time in seconds
        """
        
        return len([task for task in self.finished_tasks.values()
                   if task.start_time >= from_time and task.start_time <= to_time])

    def calculate_average_time_to_destination(self, from_time=-1, to_time=sys.maxsize):
        """
        Get the average total time the passengers have been waiting to arrive at their destination
        
        :from_time: start time in seconds
        :to_time: end time in seconds
        """

        total_times = [task.total_time for task in self.finished_tasks.values(
        ) if task.start_time >= from_time and task.start_time <= to_time]
        return statistics.mean(total_times) if total_times else None

    def calculate_average_crowdedness(self, from_time=-1, to_time=sys.maxsize):
        """
        Get the average amount of people inside an elevator
        
        :from_time: start time in seconds
        :to_time: end time in seconds
        """
                
        return statistics.mean(
            self.crowdedness[from_time:to_time]) if self.crowdedness else None

    def calculate_average_crowdedness_per_floor(self):
        """
        Get the average amount of people waiting on a floor
        """
        sorted_finish_info = sorted(
            self.finished_tasks.values(),
            key=attrgetter('start'))

        grouped_finish_info = {
            key: list(group) for key,
            group in groupby(
                sorted_finish_info,
                key=attrgetter('start'))}

        mean_values = {
            key: statistics.mean(
                info.total_time for info in group) for key,
            group in grouped_finish_info.items()}

        return mean_values

    def get_objective(self, obj: Objective, timestep=-1, timestep_amount=24):
        """
        Get some objective over an amount of time
        """
                
        max_time = max(
            [task.start_time for task in self.finished_tasks.values()])
        timestep = max_time if timestep == -1 else timestep
        result = None

        if (obj == Objective.AWT):
            result = [
                self.calculate_average_waiting_time(i * timestep, (i + 1) * timestep - 1) for i in range((max_time + timestep -1) // timestep)]
        elif (obj == Objective.AWTSD):
            result = [
                self.calculate_std_dev_waiting_time(i * timestep, (i + 1) * timestep - 1) for i in range((max_time + timestep - 1) // timestep)]
        elif (obj == Objective.ACE):
            result = [
                self.calculate_average_crowdedness(i * timestep, (i + 1) * timestep - 1) for i in range((max_time + timestep - 1) // timestep)]
        elif (obj == Objective.AMP):
            result = [
                self.calculate_amount_people_spawned(i * timestep, (i + 1) * timestep - 1) for i in range((max_time + timestep - 1) // timestep)]
        elif (obj == Objective.ATTD):
            result = [
                self.calculate_average_time_to_destination(i * timestep, (i + 1) * timestep - 1) for i in range((max_time + timestep - 1) // timestep)]

        while (len(result) < timestep_amount):
            result.append(None)
        return result if timestep != max_time else result[0]

    def get_objectives(self, objs: [Objective], timestep=-1):
        """
        Get multiple objectives over an amount of time
        """
        return [self.get_objective(obj, timestep) for obj in objs]


class FinishInfo():
    """
    All necessary statistics information of a single passenger
    """
    def __init__(self, id, start, target, start_time):
        self.id = id
        self.start = start
        self.target = target
        self.start_time = start_time
        self.waiting_time = -1
        self.total_time = -1
