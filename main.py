from simulation import Simulation,SimType, Parameter
from simulation_statistics import Objective
from building import Building
from elevator import Elevator
from policies import LOOKPolicy, SCANPolicy, FCFSPolicy, SSTFPolicy, PWDPPolicy, PWDPPolicyEnhanced
from distribution import Distribution, DistrType, TimeDistribution
from debug import Debug as DB
from color import Colors as C

floorAmount = 10
if (DB.mnStart):
    DB.pr("File","Main",message="Simulation started")
simulation = Simulation(
    Building(
            elevators = [
                Elevator(0, floorAmount-1, LOOKPolicy(), 0, 10),
            ],
            floorAmount = floorAmount,
            spawnDistribution = Distribution(floorAmount, DistrType.UNIFORM),
            targetDistribution = Distribution(floorAmount, DistrType.UNIFORM),
            timeDistribution = TimeDistribution(1, "h", [(1, 1), (1, 1)]),
            spawnEvery = 10  
        )
        ,SimType.COMPARATIVE2D,Objective.AWT,[[Parameter.DISTANCEWEIGHT,0.0,1.0,0.05]]
)
if (DB.mnSetup):
    print(simulation)

simulation.run(seconds=500)

if (DB.mnEnd):
    DB.pr("File","Main",message="Simulation ended")
