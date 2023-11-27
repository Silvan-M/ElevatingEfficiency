from simulation import Simulation
from building import Building
from elevator import Elevator
from simulation_statistics import SimulationStatistics
from simulation_statistics import Objective
from liveplotter import LivePlotter
from game_display import GameDisplay
from policies import LOOKPolicy, SCANPolicy, FCFSPolicy, SSTFPolicy, PWDPPolicy, PWDPPolicyEnhanced
from distribution import Distribution, DistrType, TimeDistribution
from debug import Debug as DB
from parameter import Parameter,TimeDistrParameter,ElevatorParameter,PolicyParameter

floorAmount = 10
if (DB.mnStart):
    DB.pr("File","Main",message="Simulation started")
simulation = Simulation(
    Building(
            elevators = [
                Elevator(0, floorAmount-1, SCANPolicy(), 20),
                Elevator(0, floorAmount-1, SCANPolicy(), 20),
            ],
            floorAmount = floorAmount,
            spawnDistribution = Distribution(floorAmount, DistrType.UNIFORM),
            targetDistribution = Distribution(floorAmount, DistrType.UNIFORM),
            timeDistribution = TimeDistribution(0.2, "h", [(1, 1), (1, 1)]),
        )
)
if (DB.mnSetup):
    print(simulation)

game = GameDisplay(simulation, 2)
livePlot = LivePlotter(simulation, [Objective.AWT, Objective.AWTSD, Objective.ACE])

simulation.run(seconds=5000, timeScale=-1)


if (DB.mnEnd):
    DB.pr("File","Main",message="Simulation ended")
