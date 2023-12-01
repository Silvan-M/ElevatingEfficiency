from parameter import Parameter
from simulation_statistics import Objective as Objective

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from datetime import datetime

class Plotter2D():
    def __init__(self, paramData:list,paramName:str, objectiveData:list,objectiveName:list,yLabel="value") -> None:
        self.paramData = paramData
        self.objectiveData = objectiveData
        self.paramName = paramName
        self.objectiveName = objectiveName
        self.yLabel=yLabel
        self.specialValues = []
        self.specialValuesName = ""

    def plotNormal(self,name:str,showMin=False,showMax=False,cmap=None,save=False,ignoreNegValue=True):
        
        plt.title(name)
        plt.xlabel(self.paramName)
        plt.ylabel(self.yLabel)

        paramDataMod = self.paramData
        for i in range(len(self.objectiveData)):
            if (ignoreNegValue):
                paramDataMod = self.paramData
                for j in reversed(range(len(self.objectiveData[i]))):
                    if (self.objectiveData[i][j]<0):
                        self.objectiveData[i].pop(j)
                        paramDataMod.pop(j)

            plt.plot(paramDataMod,self.objectiveData[i],label=self.objectiveName[i],color = self._getColor(i,len(self.objectiveData),cmap) )

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

        if (len(self.specialValues)==len(self.paramData)):
            plt.plot(self.paramData,self.specialValues,label = self.specialValuesName,color="red")

        plt.legend()

        # Display the plot
        if (save):
            current_time = datetime.now().strftime("%H_%M_%S")
            name = (str(name).lower())+"_"+str(current_time)
            plt.savefig('plotter/plots/'+str(name)+'.png')
            plt.close()
        else:
            plt.show()

    def setSpecialValue(self,specVal:list,specValName:str):
        self.specialValues  = specVal
        self.specialValuesName = specValName

    def _getColor(self, index, max,cmapInp):
        if (cmapInp==None):
            cmapInp = "viridis"
        cmap = plt.get_cmap(cmapInp)
        colors = [cmap(i) for i in np.linspace(0, 1, max)]
        return colors[max - index - 1]



