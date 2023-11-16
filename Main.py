from Simulation import Simulation
from Building import Building
from Elevator import Elevator
from Policy import BasicPolicy
from Distribution import Distribution, DistrType, TimeDistribution
from Debug import Debug as DB


floorAmount = 10

if (DB.mnStart):
    DB.pr("File","Main",message="Simulation started")

simulation = Simulation(
    Building(
            elevators = [
                Elevator(0, floorAmount, BasicPolicy()),
            ],
            floorAmount = floorAmount,
            spawnDistribution = Distribution(floorAmount, DistrType.UNIFORM),
            targetDistribution = Distribution(floorAmount, DistrType.UNIFORM),
            timeDistribution = TimeDistribution(2, "h", [(0, 0), (8,100), (10,20), (12, 100), (14, 20), (18, 100), (22, 0)])
        )
)
if (DB.mnSetup):
    print(simulation)

simulation.run(hours=24)

if (DB.mnEnd):
    DB.pr("File","Main",message="Simulation ended")