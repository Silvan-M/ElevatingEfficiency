import matplotlib.pyplot as plt
from simulation_statistics import Objective
import time
import numpy as np



import matplotlib.pyplot as plt
from simulation_statistics import Objective
import time
import numpy as np



class LivePlotter():
    def __init__(self, simulation, objectives, updateGraphInterval=1, updatePointInterval=1):
        self.objectives = objectives
        simulation.onSimulationStarted.add_listener(self.startPlot)
        simulation.onStepEnd.add_listener(self.step)
        self.updateGraphInterval = updateGraphInterval
        self.updatePointInterval = updatePointInterval
        self.fill_between_obj = None

    def startPlot(self, simulation, startTime, stepAmount):
        self.x = np.linspace(0, stepAmount, round(stepAmount / self.updatePointInterval))
        self.y = [0] * stepAmount
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
            # If AWT is also active, the standard deviation will be rendered as a band
            if objective == Objective.AWTSD and Objective.AWT in self.objectives:
                continue
            elif objective == Objective.ACE:
                # Plot Objective.ACE on the second y-axis
                self.lines[objective] = self.ax2.plot(self.x, label=str(objective.value), color=color2)[0]
            else:
                self.lines[objective] = self.ax.plot(self.x, label=str(objective.value), color=color1)[0]

        handles1, labels1 = self.ax.get_legend_handles_labels()
        handles2, labels2 = self.ax2.get_legend_handles_labels()

        self.ax.set_ylabel('Objective Value', color=color1)  # sets label and color for first y-axis
        self.ax2.set_ylabel('ACE Value', color=color2)  # sets label and color for second y-axis

        # To change the color of tick parameters to match the line color
        self.ax.tick_params(axis='y', colors=color1)
        self.ax2.tick_params(axis='y', colors=color2)

        # Create a single legend with the handles and labels from both axes
        self.ax.legend(handles1 + handles2, labels1 + labels2, loc='upper right')

        plt.show(block=False)

    def setLineData(self, objective):
        self.lines[objective].set_xdata(range(len(self.live_data[objective])))
        self.lines[objective].set_ydata(self.live_data[objective])

    def addPoints(self, simulation, tim):
        statistics = simulation.statistics

        waiters = []
        for p in statistics.finishedTasks:
            val = statistics.finishedTasks[p]
            if val.totalTime < 0:
                waiters.append(tim - val.startTime)

        if Objective.AWT in self.objectives:
            self.live_data[Objective.AWT].append(0 if len(waiters) == 0 else np.mean(waiters))
            self.setLineData(Objective.AWT)


        if Objective.AWTSD in self.objectives:
            self.live_data[Objective.AWTSD].append(0 if len(waiters) == 0 else np.std(waiters))

            # If AWT is also active, the standard deviation will be rendered as a band
            if Objective.AWT in self.objectives:
                # Remove previous fill_between if it exists
                if self.fill_between_obj is not None:
                    self.fill_between_obj.remove()

                mean_values = np.array(self.live_data[Objective.AWT])
                std_values = np.array(self.live_data[Objective.AWTSD])
                x = np.arange(len(mean_values))
                self.fill_between_obj = self.ax.fill_between(x, mean_values - std_values, mean_values + std_values, color='gray', alpha=0.2, label='Std Dev')
            else:
                self.setLineData(Objective.AWTSD)
            
        if Objective.ACE in self.objectives:
            self.live_data[Objective.ACE].append(statistics.crowdedness[-1])
            self.setLineData(Objective.ACE)
       
    def step(self, simulation, tim):
        if tim % self.updatePointInterval == 0:
            self.addPoints(simulation, tim)
            
        if tim % self.updateGraphInterval == 0 and len(self.live_data[Objective.AWT]) > 0:
            max_y = sum([max(data) for data in self.live_data.values()])
            max_y2= max(self.live_data[Objective.ACE])

            if max_y == 0:
                max_y = 1
            if max_y2 == 0:
                max_y2 = 1

            self.ax.set_ylim([0, max_y])

            self.ax2.set_ylim([0, max_y2*2])

            self.figure.canvas.draw()

            self.figure.canvas.flush_events()