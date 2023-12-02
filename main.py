from simulation import Simulation
from building import Building
from elevator import Elevator
from simulation_statistics import SimulationStatistics
from simulation_statistics import Objective
from liveplotter import LivePlotter
from game_display import GameDisplay
from policies import LOOKPolicy, SCANPolicy, FCFSPolicy, SSTFPolicy, PWDPPolicy, PWDPPolicyEnhanced
from distributions import ShoppingMallDistribution, RooftopBarDistribution, ResidentialBuildingDistribution, CustomBuildingDistribution
from debug import Debug as DB
from parameter import Parameter,TimeDistrParameter,ElevatorParameter,PolicyParameter
import random
import numpy as np

## --- START OF SETTINGS --- ##
## MAIN SETTINGS
# Show gui
showGui = True

# Show live plot
showLivePlot = True

# Set seed for random number generator (if -1, no seed is set)
seed = 1

## MAIN SCENARIO SETTINGS
# Choose whether to use a standard scenario or a custom scenario
isCustomScenario = False

# Select from one of the three standard scenarios (ShoppingMall, Rooftop, Residential)
distribution = ResidentialBuildingDistribution()

# Choose a policy for the elevators (Do not initialize the policy, only pass the class)
policy = PWDPPolicy
policyArguments = [1,1,1,1,1,1,1]

# Start simulation at a specific time
hours, minutes, seconds = 12, 0, 0


## CUSTOM SCENARIO SETTINGS
# Specify floor amount if using a custom scenario
floorAmount = 10

# Specify elevator list if using a custom scenario
elevators = [] 

# Elevator parameters: [startFloor, endFloor, policy, capacity]
# Example: [Elevator(0, floorAmount-1, SCANPolicy(), 20)]

# Window size of the GUI
windowSize = 2

## --- END OF SETTINGS --- ##

if (seed != -1):
    random.seed(seed)
    np.random.seed(seed)

if (not isCustomScenario):
    # Standard scenario, set parameters automatically
    floorAmount = distribution.floorAmount
    amountOfElevators = distribution.amountOfElevators
    for i in range(amountOfElevators):
        elevators.append(Elevator(0, floorAmount-1, policy(*policyArguments), distribution.elevatorCapacity))

    windowSize = 2//(floorAmount//10)


if (DB.mnStart):
    DB.pr("File","Main",message="Simulation started")
simulation = Simulation(
    Building(
            elevators = elevators,
            floorAmount = floorAmount,
            distribution=distribution
        )
)

# Set simulation time
simulation.setTime(hours=hours, minutes=minutes, seconds=seconds)

if (DB.mnSetup):
    print(simulation)

if (showGui):
    game = GameDisplay(simulation, windowSize)

if (showLivePlot):
    livePlot = LivePlotter(simulation, [Objective.AWT, Objective.AWTSD, Objective.ACE, Objective.AMP])

simulation.run(hours=1, timeScale=-1)


if (DB.mnEnd):
    DB.pr("File","Main",message="Simulation ended")
