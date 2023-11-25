import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import interp2d

def plot_2d_color_interpolated(x, y, z):
    # Create a grid of points for interpolation
    xi, yi = np.meshgrid(np.linspace(min(x), max(x), 100), np.linspace(min(y), max(y), 100))

    # Interpolate the Z values using interp2d
    f = interp2d(x, y, z, kind='linear')
    zi = f(xi[0, :], yi[:, 0])

    # Create a custom colormap for better color interpolation
    cmap = plt.get_cmap('viridis')

    # Create a 2D color plot
    plt.contourf(xi, yi, zi, cmap=cmap, levels=100)
    plt.colorbar(label='Z Values')

    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('2D Color Plot with Interpolation')
    plt.show()

# Example usage:
x_values = [1.0, 2.0, 3.0, 4.0, 5.0]
y_values = [2.0, 3.0, 4.0, 5.0, 6.0]
z_values =[[0.1, 0.5, 1.0, 2.0, 3.0],
    [0.2, 0.6, 1.1, 2.1, 3.1],
    [0.3, 0.7, 1.2, 2.2, 3.2],
    [0.4, 0.8, 1.3, 2.3, 3.3],
    [0.5, 0.9, 1.4, 2.4, 3.4]
]

plot_2d_color_interpolated(x_values, y_values, z_values)
