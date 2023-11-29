from simulation import Simulation
from building import Building
from elevator import Elevator
from simulation_statistics import SimulationStatistics
from simulation_statistics import Objective
from liveplotter import LivePlotter
from game_display import GameDisplay
from policies import LOOKPolicy, SCANPolicy, FCFSPolicy, SSTFPolicy, PWDPPolicy, PWDPPolicyEnhanced
from distributions import ShoppingMallDistribution, RooftopBarDistribution, ResidentialBuildingDistribution
from debug import Debug as DB
from parameter import Parameter,TimeDistrParameter,ElevatorParameter,PolicyParameter

## --- START OF SETTINGS --- ##
## MAIN SETTINGS
# Show gui
showGui = True

# Show live plot
showLivePlot = True


## MAIN SCENARIO SETTINGS
# Choose whether to use a standard scenario or a custom scenario
isCustomScenario = False

# Select from one of the three standard scenarios (ShoppingMall, Rooftop, Residential)
distribution = ShoppingMallDistribution()

# Choose a policy for the elevators
policy = SCANPolicy

# Start simulation at a specific time
hours, minutes, seconds = 13, 0, 0


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

if (not isCustomScenario):
    # Standard scenario, set parameters automatically
    floorAmount = distribution.floorAmount
    amountOfElevators = distribution.amountOfElevators
    for i in range(amountOfElevators):
        elevators.append(Elevator(0, floorAmount-1, policy(), distribution.elevatorCapacity))

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
    livePlot = LivePlotter(simulation, [Objective.AWT, Objective.AWTSD, Objective.ACE])

simulation.run(seconds=5000, timeScale=-1)


if (DB.mnEnd):
    DB.pr("File","Main",message="Simulation ended")
