from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import interp2d
from datetime import datetime

class Plotter3D():
    """
    Creates a Plotter3D object:
    - paramXData (list)    : parametric Data, will be plotted on the x-axis with label paramXName
    - paramYData  (list)   : parametric Data, will be plotted on the y-axis with label paramYName
    - objectiveData (list) : z-values of the graph in the form of a matrix m[len(paramXData)][len(paramYData)], 
                             will be labelled with objectiveName
    """
    def __init__(self,paramXData:list,paramXName:str,paramYData:list,paramYName:str,objectiveData:list,ObjectiveName:str) -> None:
        self.paramXData = paramXData
        self.paramXName = paramXName
        self.paramYData = paramYData
        self.paramYName = paramYName
        self.objectiveData = objectiveData
        self.objectiveName = ObjectiveName

    def plotNormal(self,name:str,showMin=False,showMax=False,save=False,interpolation='bilinear'):
        """
        Shows the plot with the data stored in member variables:
        - name (str)          : sets the title of the plot
        - showMin (bool)      : if True, plots and computes minimum z-value and it's corresponding x- and y-coordinate
        - showMax (bool)      : if True, plots and computes maximum z-value and it's corresponding x- and y-coordinate
        - save  (bool)        : if True, saves plot directly in plots folder with  naming "name+HH_MM_SS.png", 
                                where HH,MM,SS are hours, minutes and seconds respectively
        - interpolation (str) : chooses interpolation mode, options are: 
                                'none', 'nearest', 'bilinear', 'bicubic', 'spline16',
                                'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
                                'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos'
        
        """

        if save:
            # Force matplotlib to not use any Xwindows backend, to guarantee thread safety. 
            matplotlib.use('Agg')
            plt.ioff()

        xi, yi = np.meshgrid(np.linspace(min(self.paramXData), max(self.paramXData),len(self.paramXData)), 
                             np.linspace(min(self.paramYData), max(self.paramYData), len(self.paramXData)))

        # Interpolate the Z values using interp2d
        f = interp2d(self.paramXData, self.paramYData, self.objectiveData, kind='linear')
        zi = f(xi[0, :], yi[:, 0])

        # chooses cmap
        cmap = plt.get_cmap('viridis')

        # Use imshow to create a rasterized 2D plot
        plt.imshow(zi, extent=(np.amin(xi), np.amax(xi), np.amin(yi), np.amax(yi)), origin='lower', cmap=cmap, aspect='auto', interpolation=interpolation)
        plt.colorbar(label=str(self.objectiveName))


        # computes and plots maximum, if showMax
        if showMax:
            max_z_index = np.unravel_index(np.argmax(zi, axis=None), zi.shape)
            max_z_x = xi[max_z_index]
            max_z_y = yi[max_z_index]

            round_max_z_x = round(max_z_x, 2)
            round_max_z_y = round(max_z_y, 2)

            print("[Plotter3D] Maximum was found at ("+str(round_max_z_x)+","+str(round_max_z_y)+")")
            plt.plot(max_z_x, max_z_y, marker='x', color='red', label="M("+str(round_max_z_x)+","+str(round_max_z_y)+")")

        # computes and plots maximum, if showMin
        if showMin:
            min_z_index = np.unravel_index(np.argmin(zi, axis=None), zi.shape)
            min_z_x = xi[min_z_index]
            min_z_y = yi[min_z_index]
            
            round_min_z_x = round(min_z_x, 2)
            round_min_z_y = round(min_z_y, 2)

            print("[Plotter3D] Maximum was found at ("+str(round_min_z_x)+","+str(round_min_z_y)+")") 
            plt.plot(min_z_x, min_z_y, marker='x', color='blue', label="m("+str(round_min_z_x)+","+str(round_min_z_y)+")")

        plt.legend()
        plt.xlabel(str(self.paramXName))
        plt.ylabel(str(self.paramYName))
        plt.title(name)
        if (save):
            current_time = datetime.now().strftime("%H_%M_%S")
            name = (str(name).lower())+"_"+str(current_time)
            plt.savefig('plotter/plots/'+str(name)+'.pdf')
            plt.close()
        else:
            plt.show()

