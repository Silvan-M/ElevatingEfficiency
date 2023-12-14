import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import copy
from datetime import datetime


class Plotter2D():
    """
    Creates a Plotter2D object:
    - param_data (list)     : parametric Data, will be plotted on the x-axis with label param_name
    - objective_data (list) : multiple curves, each stored by y-values in the form of a objective_data[i] = list[len(param_data)],
                             will be labelled with respective objective_name[i]
    - spec_val (list)       : special values will be plotted in red and labelled spec_val_name
    """

    def __init__(
            self,
            param_data: list,
            param_name: str,
            objective_data: list,
            objective_name: list,
            y_label="value",
            spec_val=[],
            spec_val_name="") -> None:

        self.param_data = param_data
        self.objective_data = objective_data
        self.param_name = param_name
        self.objective_name = objective_name
        self.y_label = y_label
        self.special_values = spec_val
        self.special_values_name = spec_val_name

    def plot_normal(
            self,
            name: str,
            show_min=False,
            show_max=False,
            cmap=None,
            save=False,
            ignore_neg_value=True,
            max_val=None):
        """
        Shows the plot with the data stored in member variables:
        - name (str)            : sets the title of the plot
        - show_min (bool)        : if True, plots and computes minimum z-value and it's corresponding x- and y-coordinate
        - show_max (bool)        : if True, plots and computes maximum z-value and it's corresponding x- and y-coordinate
        - cmap (str)            : sets cmap, which defines color. Options: https://matplotlib.org/stable/users/explain/colors/colormaps.html
        - save  (bool)          : if True, saves plot directly in plots folder with  naming "name+HH_MM_SS.pdf",
                                  where HH,MM,SS are hours, minutes and seconds respectively
        - ignore_neg_value (bool) : if True, automatically ignores negative values. simulatiom_plotter.py marks None with -1
                                  This might occur when the distribution is really low and no passengers spawn and thus
                                  AWT, ATTD and average crowdedness are undefined

        """

        plt.title(name)
        plt.xlabel(self.param_name)
        plt.ylabel(self.y_label)

        if save:
            plt.ioff()

        param_data_mod = copy.deepcopy(self.param_data)

        for i in range(len(self.objective_data)):
            if (ignore_neg_value):

                # creates (unlinked) copy fo param_data, which is modified in
                # the case a negative value gets ignored

                param_data_mod = copy.deepcopy(self.param_data)

                # checks if value is negative and then pops x and according
                # y-value

                for j in reversed(range(len(self.objective_data[i]))):
                    if (self.objective_data[i][j] < 0):
                        self.objective_data[i].pop(j)
                        param_data_mod.pop(j)
            plt.plot(param_data_mod,
                     self.objective_data[i],
                     label=self.objective_name[i],
                     color=self._get_color(i,
                                          len(self.objective_data),
                                          cmap))

        # Find and mark the maximum value, if show_max

        if (show_max):
            max_values = [max(data) for data in self.objective_data]
            max_indices = [np.argmax(data) for data in self.objective_data]
            for idx, max_val, max_idx in zip(
                    range(len(self.objective_data)), max_values, max_indices):
                plt.scatter(
                    self.param_data[max_idx],
                    max_val,
                    color='red',
                    marker='o',
                    label="maximum")

        # Find and mark the minimum value, if show_min

        if (show_min):
            min_values = [min(data) for data in self.objective_data]
            min_indices = [np.argmin(data) for data in self.objective_data]
            for idx, min_val, min_idx in zip(
                    range(len(self.objective_data)), min_values, min_indices):
                plt.scatter(
                    self.param_data[min_idx],
                    min_val,
                    color='blue',
                    marker='o',
                    label="minimum")

        # Plots special values, if special_values is non-empty
        if (len(self.special_values) == len(self.param_data)):
            plt.plot(
                self.param_data,
                self.special_values,
                label=self.special_values_name,
                color="red")

        plt.legend()

        if max_val is not None:
            plt.xlim(0, max_val)

        # Display or save the plot
        if (save):
            current_time = datetime.now().strftime("%H_%M_%S")
            name = (str(name).lower()) + "_" + str(current_time)
            plt.savefig('plotter/plots/' + str(name) + '.pdf')
            plt.close()
        else:
            plt.show()

    def _get_color(self, index, max, cmap_inp):
        """
        Returns the color according to the color-map (cmap).
        - index (int)        : selects which color gets returned
        - max (int)          : sets the range of the cmap
        - cmap_inp (str,None) : selects cmap and if None, sets cmap to "viridis"

        """
        if (cmap_inp is None):
            cmap_inp = "winter"
        cmap = plt.get_cmap(cmap_inp)
        colors = [cmap(i) for i in np.linspace(0, 1, max)]
        return colors[max - index - 1]
