import matplotlib.pyplot as plt
from simulation_statistics import Objective
import time
import numpy as np


import matplotlib.pyplot as plt
from simulation_statistics import Objective
import time
import numpy as np


class LivePlotter():
    """
    Live plotter for the simulation

    :param simulation: simulation to plot
    :type simulation: Simulation
    :param objectives: objectives to plot
    :type objectives: list[Objective]
    :param update_graph_interval: interval to update the graph
    :type update_graph_interval: int
    :param update_point_interval: interval to update the points
    :type update_point_interval: int
    """


    def __init__(
            self,
            simulation,
            objectives,
            update_graph_interval=1,
            update_point_interval=1):
        self.objectives = objectives
        simulation.on_simulation_started.add_listener(self.start_plot)
        simulation.on_step_end.add_listener(self.step)
        self.update_graph_interval = update_graph_interval
        self.update_point_interval = update_point_interval
        self.fill_between_obj = None

    def start_plot(self, simulation, start_time, step_amount):
        """
        Starts the plotter

        :param simulation: simulation to plot
        :type simulation: Simulation
        :param start_time: start time of the simulation
        :type start_time: int
        :param step_amount: amount of steps in the simulation
        :type step_amount: int
        """
        self.x = np.linspace(
            0, step_amount, round(
                step_amount / self.update_point_interval))
        self.y = [0] * step_amount
        plt.ion()

        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.ax2 = self.ax.twinx()  # Create a second y-axis

        plt.title("Elevating Efficiency", fontsize=25)
        self.ax.set_xlabel("Time", fontsize=18)
        self.live_data = {objective: [] for objective in self.objectives}

        color1 = 'firebrick'
        color2 = 'steelblue'

        self.lines = {}
        for objective in self.objectives:
            # If AWT is also active, the standard deviation will be rendered as
            # a band
            if objective == Objective.AWTSD and Objective.AWT in self.objectives:
                continue
            elif objective == Objective.ACE:
                # Plot Objective.ACE on the second y-axis
                self.lines[objective] = self.ax2.plot(
                    self.x, label=str(objective.value), color=color2)[0]
            else:
                self.lines[objective] = self.ax.plot(
                    self.x, label=str(objective.value), color=color1)[0]

        handles1, labels1 = self.ax.get_legend_handles_labels()
        handles2, labels2 = self.ax2.get_legend_handles_labels()

        # sets label and color for first y-axis
        self.ax.set_ylabel('Objective Value', color=color1)
        # sets label and color for second y-axis
        self.ax2.set_ylabel('ACE Value', color=color2)

        # To change the color of tick parameters to match the line color
        self.ax.tick_params(axis='y', colors=color1)
        self.ax2.tick_params(axis='y', colors=color2)

        # Create a single legend with the handles and labels from both axes
        self.ax.legend(
            handles1 + handles2,
            labels1 + labels2,
            loc='upper right')

        plt.show(block=False)

    def set_line_data(self, objective):
        """
        Sets the data of a line

        :param objective: objective to set the data of
        :type objective: Objective
        """
        self.lines[objective].set_xdata(range(len(self.live_data[objective])))
        self.lines[objective].set_ydata(self.live_data[objective])

    def add_points(self, simulation, tim):
        """
        Adds points to the plot

        :param simulation: simulation to plot
        :type simulation: Simulation
        :param tim: current time
        :type tim: int
        """
        statistics = simulation.statistics

        waiters = []
        for p in statistics.finished_tasks:
            val = statistics.finished_tasks[p]
            if val.total_time < 0:
                waiters.append(tim - val.start_time)

        if Objective.AWT in self.objectives:
            self.live_data[Objective.AWT].append(
                0 if len(waiters) == 0 else np.mean(waiters))
            self.set_line_data(Objective.AWT)

        if Objective.AWTSD in self.objectives:
            self.live_data[Objective.AWTSD].append(
                0 if len(waiters) == 0 else np.std(waiters))

            # If AWT is also active, the standard deviation will be rendered as
            # a band
            if Objective.AWT in self.objectives:
                # Remove previous fill_between if it exists
                if self.fill_between_obj is not None:
                    self.fill_between_obj.remove()

                mean_values = np.array(self.live_data[Objective.AWT])
                std_values = np.array(self.live_data[Objective.AWTSD])
                x = np.arange(len(mean_values))
                self.fill_between_obj = self.ax.fill_between(
                    x,
                    mean_values -
                    std_values,
                    mean_values +
                    std_values,
                    color='gray',
                    alpha=0.2,
                    label='Std Dev')
            else:
                self.set_line_data(Objective.AWTSD)

        if Objective.ACE in self.objectives:
            self.live_data[Objective.ACE].append(statistics.crowdedness[-1])
            self.set_line_data(Objective.ACE)

        if Objective.AMP in self.objectives:
            self.live_data[Objective.AMP].append(
                statistics.calculate_amount_people_spawned())
            self.set_line_data(Objective.AMP)

    def step(self, simulation, tim):
        """
        Steps the plotter

        :param simulation: simulation to plot
        :type simulation: Simulation
        :param tim: current time
        :type tim: int
        """


        if tim % self.update_point_interval == 0:
            self.add_points(simulation, tim)

        if tim % self.update_graph_interval == 0 and len(
                self.live_data[Objective.AWT]) > 0:
            max_y = sum([max(data) for data in self.live_data.values()])
            max_y2 = max(self.live_data[Objective.ACE])

            if max_y == 0:
                max_y = 1
            if max_y2 == 0:
                max_y2 = 1

            self.ax.set_ylim([0, max_y])

            self.ax2.set_ylim([0, max_y2 * 2])

            self.figure.canvas.draw()

            self.figure.canvas.flush_events()
