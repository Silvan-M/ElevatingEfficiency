from parameter import Parameter
from simulation_statistics import Objective as Objective

import matplotlib.pyplot as plt

class Plotter2D():
    def __init__(self, paramData:list,paramName:str, objectiveData:list,objectiveName:str) -> None:
        self.paramData = paramData
        self.objectiveData = objectiveData
        self.paramName = paramName
        self.objectiveName = objectiveName

    def plotNormal(self):
        
        plt.title("TODO")
        plt.xlabel(self.paramName)
        plt.ylabel(self.objectiveName)
        plt.plot(self.paramData,self.objectiveData)
        plt.legend()

        # Display the plot
        plt.show()



