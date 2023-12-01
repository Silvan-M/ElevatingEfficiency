from mpl_toolkits.mplot3d import Axes3D
from simulation_statistics import Objective as Objective

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import interp2d
from datetime import datetime

class Plotter3D():
    def __init__(self,param1Data:list,param1Name:str,param2Data:list,param2Name:str,objectiveData:list,ObjectiveName:str) -> None:
        self.param1Data = param1Data
        self.param1Name = param1Name
        self.param2Data = param2Data
        self.param2Name = param2Name
        self.objectiveData = objectiveData
        self.objectiveName = ObjectiveName

    


    def plotNormal(self,name:str,showMin=False,showMax=False,save=False,interpolation='bilinear'):
        xi, yi = np.meshgrid(np.linspace(min(self.param1Data), max(self.param1Data),len(self.param1Data)), 
                             np.linspace(min(self.param2Data), max(self.param2Data), len(self.param1Data)))

        # Interpolate the Z values using interp2d
        f = interp2d(self.param1Data, self.param2Data, self.objectiveData, kind='linear')
        zi = f(xi[0, :], yi[:, 0])

        cmap = plt.get_cmap('viridis')

        # Use imshow to create a rasterized 2D plot
        plt.imshow(zi, extent=(np.amin(xi), np.amax(xi), np.amin(yi), np.amax(yi)), origin='lower', cmap=cmap, aspect='auto', interpolation=interpolation)
        plt.colorbar(label=str(self.objectiveName))


        if showMax:
            max_z_index = np.unravel_index(np.argmax(zi, axis=None), zi.shape)
            max_z_x = xi[max_z_index]
            max_z_y = yi[max_z_index]

            round_max_z_x = round(max_z_x, 2)
            round_max_z_y = round(max_z_y, 2)

            print("[Plotter3D] Maximum was found at ("+str(round_max_z_x)+","+str(round_max_z_y)+")")
            plt.plot(max_z_x, max_z_y, marker='x', color='red', label="M("+str(round_max_z_x)+","+str(round_max_z_y)+")")

        if showMin:
            min_z_index = np.unravel_index(np.argmin(zi, axis=None), zi.shape)
            min_z_x = xi[min_z_index]
            min_z_y = yi[min_z_index]
            
            round_min_z_x = round(min_z_x, 2)
            round_min_z_y = round(min_z_y, 2)

            print("[Plotter3D] Maximum was found at ("+str(round_min_z_x)+","+str(round_min_z_y)+")") 
            plt.plot(min_z_x, min_z_y, marker='x', color='blue', label="m("+str(round_min_z_x)+","+str(round_min_z_y)+")")

        plt.legend()
        plt.xlabel(str(self.param1Name))
        plt.ylabel(str(self.param2Name))
        plt.title(name)
        if (save):
            current_time = datetime.now().strftime("%H_%M_%S")
            name = (str(name).lower())+"_"+str(current_time)
            plt.savefig('plotter/plots/'+str(name)+'.png')
            plt.close()
        else:
            plt.show()


