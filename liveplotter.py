import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
from simulation_statistics import Objective
import time
import numpy as np
from enum import Enum



class LivePlotter():
    def __init__(self, simulation, objectives):
        self.objectives = objectives
        simulation.onSimulationStarted.add_listener(self.startPlot)
        simulation.onStepEnd.add_listener(self.step)


    def startPlot(self, simulation, stepAmount):
        self.x = np.linspace(0, stepAmount, stepAmount)
        self.y = [10] * stepAmount
        plt.ion()

        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.live_data = {objective: [] for objective in self.objectives}

        self.lines = {}
        for objective in self.objectives:
            self.lines[objective] = self.ax.plot(self.x, label=str(objective.value))[0]

        self.ax.legend()

        plt.title("Elevating Efficiency", fontsize=25)

        plt.xlabel("Time", fontsize=18)
        plt.ylabel("", fontsize=18)
        plt.show()  # Display the plot

       
    def step(self, simulation, tim):
        statistics = simulation.statistics
        building = simulation.building

        new_data_points = {}

        waiters = []
        for p in statistics.finishedTasks:
            val = statistics.finishedTasks[p]
            if val.totalTime < 0:
                waiters.append(tim - val.startTime)

        if Objective.AWT in self.objectives:
            new_data_points[Objective.AWT] = 0 if len(waiters) == 0 else np.mean(waiters)

        if Objective.AWTSD in self.objectives:
            new_data_points[Objective.AWTSD] = 0 if len(waiters) == 0 else np.std(waiters)

        if Objective.ACE in self.objectives:
            count = sum(len(e.passengerList) for e in building.elevators)
            new_data_points[Objective.ACE] = count / len(building.elevators)

        for objective in self.objectives:
            self.live_data[objective].append(new_data_points[objective])

        for objective in self.objectives:
            self.lines[objective].set_xdata(range(len(self.live_data[objective])))
            self.lines[objective].set_ydata(self.live_data[objective])
        
        min_y = min([min(data) for data in self.live_data.values()])
        max_y = max([max(data) for data in self.live_data.values()])
        self.ax.set_ylim(min_y, max_y)
        self.figure.canvas.draw()

        self.figure.canvas.flush_events()

        



