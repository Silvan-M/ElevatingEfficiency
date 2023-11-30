import matplotlib.pyplot as plt
from simulation_statistics import Objective
import time
import numpy as np



class LivePlotter():
    def __init__(self, simulation, objectives):
        self.objectives = objectives
        simulation.onSimulationStarted.add_listener(self.startPlot)
        simulation.onStepEnd.add_listener(self.step)


    def startPlot(self, simulation, startTime, stepAmount):
        self.x = np.linspace(0, stepAmount, stepAmount)
        self.y = [0] * stepAmount
        plt.ion()

        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        plt.title("Elevating Efficiency", fontsize=25)
        plt.xlabel("Time", fontsize=18)
        self.live_data = {objective: [] for objective in self.objectives}

        self.lines = {}
        for objective in self.objectives:
            # If AWT is also active, the standard deviation will be rendered as a band
            if objective == Objective.AWTSD and Objective.AWT in self.objectives:
                continue

            self.lines[objective] = self.ax.plot(self.x, label=str(objective.value))[0]

        self.ax.legend()
        plt.show()  # Display the plot

    def setLineData(self, objective):
        self.lines[objective].set_xdata(range(len(self.live_data[objective])))
        self.lines[objective].set_ydata(self.live_data[objective])
       
    def step(self, simulation, tim):
        statistics = simulation.statistics
        building = simulation.building

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
                mean_values = np.array(self.live_data[Objective.AWT])
                std_values = np.array(self.live_data[Objective.AWTSD])
                x = np.arange(len(mean_values))
                self.ax.fill_between(x, mean_values - std_values, mean_values + std_values, color='green', alpha=0.02, label='Std Dev')
            else:
                self.setLineData(Objective.AWTSD)
            
        if Objective.ACE in self.objectives:
            self.live_data[Objective.ACE].append(statistics.crowdedness[-1])
            self.setLineData(Objective.ACE)
        
        max_y = sum([max(data) for data in self.live_data.values()])

        self.ax.set_ylim(0, max_y)
        self.figure.canvas.draw()

        self.figure.canvas.flush_events()