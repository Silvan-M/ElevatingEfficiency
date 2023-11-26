from simulation import Simulation
from building import Building
from elevator import Elevator
from simulation_statistics import SimulationStatistics
from plotter import Objective
from plotter import LivePlotter
from game_display import GameDisplay
from policies import LOOKPolicy, SCANPolicy, FCFSPolicy, SSTFPolicy, PWDPPolicy, PWDPPolicyEnhanced
from distribution import Distribution, DistrType, TimeDistribution
from debug import Debug as DB

floorAmount = 10
if (DB.mnStart):
    DB.pr("File","Main",message="Simulation started")

simulation = Simulation(
    Building(
            elevators = [
                Elevator(0, floorAmount-1, LOOKPolicy(), 0, 10),
                Elevator(0, floorAmount-1, LOOKPolicy(), 1, 10),
            ],
            floorAmount = floorAmount,
            spawnDistribution = Distribution(floorAmount, DistrType.UNIFORM),
            targetDistribution = Distribution(floorAmount, DistrType.UNIFORM),
            timeDistribution = TimeDistribution(1, "h", [(1, 1), (1, 1)]),
            spawnEvery = 10
        )
)
if (DB.mnSetup):
    print(simulation)

game = GameDisplay(simulation, 2)
plot = SimulationStatistics(simulation, [LivePlotter(simulation, [Objective.AWT, Objective.AWTSD, Objective.ACE])])

simulation.run(seconds=500, timeScale=.01)


if (DB.mnEnd):
    DB.pr("File","Main",message="Simulation ended")
