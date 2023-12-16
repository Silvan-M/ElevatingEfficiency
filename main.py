from simulation import Simulation
from building import Building
from elevator import Elevator
from simulation_statistics import SimulationStatistics
from simulation_statistics import Objective
from liveplotter import LivePlotter
from game_display import GameDisplay
from debug import Debug as DB
from parameter import Parameter, TimeDistrParameter, ElevatorParameter, PolicyParameter
import policies
import distributions
import random
import numpy as np

## --- START OF SETTINGS --- ##
# MAIN SETTINGS
# Show gui
show_gui = True
start_paused = False

# Show live plot
show_live_plot = True

# Set seed for random number generator (if -1, no seed is set)
seed = -1

# MAIN SCENARIO SETTINGS
# Choose whether to use a standard scenario or a custom scenario
is_custom_scenario = False

# Select from one of the three standard scenarios (ShoppingMall, Rooftop, Residential), initialize the distribution
distribution = distributions.ResidentialBuildingDistribution()

# Choose a policy for the elevators (Do not initialize the policy, only pass the class)
policy = policies.PWDPPolicy
policy_arguments = []

# Start simulation at a specific time
hours, minutes, seconds = 12, 0, 0


# CUSTOM SCENARIO SETTINGS
# Specify floor amount if using a custom scenario
floor_amount = 10

# Specify elevator list if using a custom scenario
elevators = []

# Elevator parameters: [startFloor, endFloor, policy, capacity]
# Example: [Elevator(0, floor_amount-1, SCANPolicy(), 20)]

# Window size of the GUI
window_size = 2

## --- END OF SETTINGS --- ##

if (seed != -1):
    random.seed(seed)
    np.random.seed(seed)

if (not is_custom_scenario):
    # Standard scenario, set parameters automatically
    floor_amount = distribution.floor_amount
    amount_of_elevators = distribution.amount_of_elevators
    for i in range(amount_of_elevators):
        elevators.append(
            Elevator(
                0,
                floor_amount - 1,
                policy(
                    *policy_arguments),
                distribution.elevator_capacity))

    window_size = 2 // (floor_amount // 10)


if (DB.mn_start):
    DB.pr("File", "Main", message="Simulation started")
simulation = Simulation(
    Building(
        elevators=elevators,
        floor_amount=floor_amount,
        distribution=distribution
    )
)

# Set simulation time
simulation.set_time(hours=hours, minutes=minutes, seconds=seconds)

if (DB.mn_setup):
    print(simulation)

if (show_gui):
    game = GameDisplay(simulation, window_size, start_paused)

if (show_live_plot):
    livePlot = LivePlotter(
        simulation, [
            Objective.AWT, Objective.AWTSD, Objective.ACE])

simulation.run(hours=1, time_scale=-1)


if (DB.mnEnd):
    DB.pr("File", "Main", message="Simulation ended")
