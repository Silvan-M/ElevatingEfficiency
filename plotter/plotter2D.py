import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import copy
from datetime import datetime

class Plotter2D():
    """
    Creates a Plotter2D object:
    - paramData (list)     : parametric Data, will be plotted on the x-axis with label paramName
    - objectiveData (list) : multiple curves, each stored by y-values in the form of a objectiveData[i] = list[len(paramData)], 
                             will be labelled with respective objectiveName[i]
    - specVal (list)       : special values will be plotted in red and labelled specValName
    """
    def __init__(self, paramData:list,paramName:str, objectiveData:list,objectiveName:list,yLabel="value",specVal=[],specValName="") -> None:

        self.paramData = paramData
        self.objectiveData = objectiveData
        self.paramName = paramName
        self.objectiveName = objectiveName
        self.yLabel=yLabel
        self.specialValues = specVal
        self.specialValuesName = specValName

    def plotNormal(self,name:str,showMin=False,showMax=False,cmap=None,save=False,ignoreNegValue=True):
        """
        Shows the plot with the data stored in member variables:
        - name (str)            : sets the title of the plot
        - showMin (bool)        : if True, plots and computes minimum z-value and it's corresponding x- and y-coordinate
        - showMax (bool)        : if True, plots and computes maximum z-value and it's corresponding x- and y-coordinate
        - cmap (str)            : sets cmap, which defines color. Options: https://matplotlib.org/stable/users/explain/colors/colormaps.html
        - save  (bool)          : if True, saves plot directly in plots folder with  naming "name+HH_MM_SS.pdf", 
                                  where HH,MM,SS are hours, minutes and seconds respectively
        - ignoreNegValue (bool) : if True, automatically ignores negative values. simulatiom_plotter.py marks None with -1
                                  This might occur when the distribution is really low and no passengers spawn and thus 
                                  AWT, ATTD and average crowdedness are undefined 
        
        """
        
        plt.title(name)
        plt.xlabel(self.paramName)
        plt.ylabel(self.yLabel)
        

        paramDataMod = copy.deepcopy(self.paramData)

        for i in range(len(self.objectiveData)):
            if (ignoreNegValue):

                # creates (unlinked) copy fo paramData, which is modified in the case a negative value gets ignored

                paramDataMod = copy.deepcopy(self.paramData)
                 
                # checks if value is negative and then pops x and according y-value
                
                for j in reversed(range(len(self.objectiveData[i]))):
                    if (self.objectiveData[i][j]<0):
                        self.objectiveData[i].pop(j)
                        paramDataMod.pop(j)
            plt.plot(paramDataMod,self.objectiveData[i],label=self.objectiveName[i],color = self._getColor(i,len(self.objectiveData),cmap) )

        # Find and mark the maximum value, if showMax

        if (showMax):
            max_values = [max(data) for data in self.objectiveData]
            max_indices = [np.argmax(data) for data in self.objectiveData]
            for idx, max_val, max_idx in zip(range(len(self.objectiveData)), max_values, max_indices):
                plt.scatter(self.paramData[max_idx], max_val, color='red', marker='o',label = "maximum")

        # Find and mark the minimum value, if showMin

        if (showMin):
            min_values = [min(data) for data in self.objectiveData]
            min_indices = [np.argmin(data) for data in self.objectiveData]
            for idx, min_val, min_idx in zip(range(len(self.objectiveData)), min_values, min_indices):
                plt.scatter(self.paramData[min_idx], min_val, color='blue', marker='o',label="minimum")


        # Plots special values, if specialValues is non-empty
        if (len(self.specialValues)==len(self.paramData)):
            plt.plot(self.paramData,self.specialValues,label = self.specialValuesName,color="red")

        plt.legend()

        # Display or save the plot
        if (save):
            current_time = datetime.now().strftime("%H_%M_%S")
            name = (str(name).lower())+"_"+str(current_time)
            plt.savefig('plotter/plots/'+str(name)+'.pdf')
            plt.close()
        else:
            plt.show()

    def _getColor(self, index, max,cmapInp):
        """
        Returns the color according to the color-map (cmap).
        - index (int)        : selects which color gets returned
        - max (int)          : sets the range of the cmap
        - cmapInp (str,None) : selects cmap and if None, sets cmap to "viridis"
        
        """
        if (cmapInp==None):
            cmapInp = "viridis"
        cmap = plt.get_cmap(cmapInp)
        colors = [cmap(i) for i in np.linspace(0, 1, max)]
        return colors[max - index - 1]





