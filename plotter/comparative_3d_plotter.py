from mpl_toolkits.mplot3d import Axes3D
from simulation_statistics import Objective as Objective

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import interp2d

class Comparative_3d_plotter():
    def __init__(self,objective:Objective, objectiveData:list, param1Data:list,param2Data:list) -> None:
        self.param1Data = param1Data
        self.param2Data = param2Data
        self.objectiveData = objectiveData
        self.objective = objective
        


    def plotNormal(self):
        xi, yi = np.meshgrid(np.linspace(min(self.param1Data), max(self.param1Data),len(self.param1Data)), np.linspace(min(self.param2Data), max(self.param2Data), len(self.param1Data)))

        # Interpolate the Z values using interp2d
        f = interp2d(self.param1Data, self.param2Data, self.objectiveData, kind='linear')
        zi = f(xi[0, :], yi[:, 0])

        cmap = plt.get_cmap('viridis')


        plt.contourf(xi, yi, zi, cmap=cmap, levels=1000)
        plt.colorbar(label='Z Values')

        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.title('2D Color Plot with Interpolation')
        plt.show()

