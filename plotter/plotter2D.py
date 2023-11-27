from parameter import Parameter
from simulation_statistics import Objective as Objective

import matplotlib.pyplot as plt

class Plotter2D():
    def __init__(self, paramData:list,paramName:str, objectiveData:list,objectiveName:list) -> None:
        self.paramData = paramData
        self.objectiveData = objectiveData
        self.paramName = paramName
        self.objectiveName = objectiveName

    def plotNormal(self):
        print(self.objectiveData)
        
        plt.title("TODO")
        plt.xlabel(self.paramName)
        plt.ylabel("value")
        for i in range(len(self.objectiveData)):
            plt.plot(self.paramData,self.objectiveData[i],label=self.objectiveName[i])
        plt.legend()

        # Display the plot
        plt.show()



