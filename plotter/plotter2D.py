from parameter import Parameter
from simulation_statistics import Objective as Objective

import matplotlib.pyplot as plt
import numpy as np

class Plotter2D():
    def __init__(self, paramData:list,paramName:str, objectiveData:list,objectiveName:list) -> None:
        self.paramData = paramData
        self.objectiveData = objectiveData
        self.paramName = paramName
        self.objectiveName = objectiveName

    def plotNormal(self,showMin=False,showMax=False):
        print(self.objectiveData)
        
        plt.title("TODO")
        plt.xlabel(self.paramName)
        plt.ylabel("value")
        for i in range(len(self.objectiveData)):
            plt.plot(self.paramData,self.objectiveData[i],label=self.objectiveName[i])

        # Find and mark the maximum value

        if (showMax):
            max_values = [max(data) for data in self.objectiveData]
            max_indices = [np.argmax(data) for data in self.objectiveData]
            for idx, max_val, max_idx in zip(range(len(self.objectiveData)), max_values, max_indices):
                plt.scatter(self.paramData[max_idx], max_val, color='red', marker='o',label = "maximum")

        # Find and mark the minimum value

        if (showMin):
            min_values = [min(data) for data in self.objectiveData]
            min_indices = [np.argmin(data) for data in self.objectiveData]
            for idx, min_val, min_idx in zip(range(len(self.objectiveData)), min_values, min_indices):
                plt.scatter(self.paramData[min_idx], min_val, color='blue', marker='o',label="minimum")
        plt.legend()

        # Display the plot
        plt.show()



