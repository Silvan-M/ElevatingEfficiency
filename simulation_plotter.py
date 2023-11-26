from policies import Policy
from policies import LOOKPolicy, SCANPolicy, FCFSPolicy, SSTFPolicy, PWDPPolicy, PWDPPolicyEnhanced
from distribution import Distribution, DistrType, TimeDistribution
from debug import Debug as DB
from exceptions import Exceptions as EXC

class SimulationPlotter():
    def __init__(
        self,elevatorArgs=[[0, 9, LOOKPolicy(), 0, 10]], 
        floorAmount = 10, 
        spawnDistrArgs=[10, DistrType.UNIFORM],
        targetDistrArgs=[10, DistrType.UNIFORM],
        timeDistrArgs = [1, "h", [(1, 1), (1, 1)]],
        spawnEveryArgs = 10) -> None:
        
        self.floorAmount = floorAmount
        self.elevatorArgs = elevatorArgs
        self.spawnDistrArgs=spawnDistrArgs
        self.targetDistrArgs=targetDistrArgs
        self.timeDistrArgs = timeDistrArgs 
        self.spawnEveryArgs = spawnEveryArgs



    def compparative_2d_plotter(self):
        pass

    def comparative_3d_plotter(self):
        pass

    def _setFloorAmount(self,amount:int):
        self.floorAmount = amount
        self.spawnDistrArgs[0] = amount
        self.timeDistrArgs[0] = amount

        for i in range(len(self.elevatorArgs)):
            self.elevatorArgs[i][1]=amount-1

    def _updateParam():
        pass

    def _addElevator(self,args:list):
        EXC.typeChecker("simulation plotter",args,[int, int, Policy,int,int])

        self.elevatorArgs.append(args)
        pass
    def _updateElevator(self):
        pass
    def _updateSpawnDistr(self):
        pass
    def _updateTargetDistr(self):
        pass
    def _updateTimeDistr(self):
        pass





