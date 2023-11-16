from Simulation import Simulation
from Building import Building
from Elevator import Elevator
from Policy import BasicPolicy
from Distribution import Distribution, DistrType
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
            timeDistribution = None
        )
)
if (DB.mnSetup):
    print(simulation)

simulation.run(minutes=10)

if (DB.mnEnd):
    DB.pr("File","Main",message="Simulation ended")