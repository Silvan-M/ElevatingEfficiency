from simulation import Simulation,SimType, Parameter
from simulation_statistics import Objective
from game_display import GameDisplay
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
    [
             [
                [0, floorAmount-1, LOOKPolicy(), 0, 10]
            ],
            floorAmount,
            [floorAmount, DistrType.UNIFORM],
            [floorAmount, DistrType.UNIFORM],
            [1, "h", [(1, 1), (1, 1)]],
            10  
    ]
        ,SimType.COMPARATIVE2D,Objective.AWT,[[Parameter.ELEVCAPACITY,0.0,10.0,1.0]])
if (DB.mnSetup):
    print(simulation)

game = GameDisplay(simulation, 2)

simulation.run(seconds=500)

if (DB.mnEnd):
    DB.pr("File","Main",message="Simulation ended")
