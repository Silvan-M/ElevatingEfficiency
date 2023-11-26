from parameter import Parameter
from simulation_statistics import Objective as Objective

import matplotlib.pyplot as plt

class Comparative_2d_plotter():
    def __init__(self, paramData:list, objectiveData:list,name:list) -> None:
        self.paramData = paramData
        self.objectiveData = objectiveData
        self.name = name 

    def plotNormal(self):
        
        plt.title("TODO")
        plt.xlabel('param')
        plt.ylabel(self.objective.value)
        plt.plot(self.objectiveData,self.paramData)
        plt.legend()

        # Display the plot
        plt.show()



