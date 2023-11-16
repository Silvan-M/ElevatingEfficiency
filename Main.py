from Simulation import Simulation
from Building import Building
from Elevator import Elevator
from Policy import Policy
from Distribution import Distribution, DistrType

floorAmount = 10
simulation = Simulation(
    Building(
            elevators = [
                Elevator(0, floorAmount, Policy())
            ],
            floorAmount = floorAmount,
            spawnDistribution = Distribution(floorAmount, DistrType.UNIFORM),
            targetDistribution = Distribution(floorAmount, DistrType.UNIFORM),
            timeDistribution = None
        )
)

simulation.run(minutes=1)