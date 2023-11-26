from simulation import Simulation
from building import Building
from elevator import Elevator
from policies import Policy
from policies import LOOKPolicy, SCANPolicy, FCFSPolicy, SSTFPolicy, PWDPPolicy, PWDPPolicyEnhanced
from distribution import Distribution, DistrType, TimeDistribution
from debug import Debug as DB
from parameter import Parameter,ElevatorParameter,TimeDistrParameter, PolicyParameter
from exceptions import Exceptions as EXC

class SimulationPlotter():
    def __init__(
        self,
        elevatorArgs=[[0, 9, LOOKPolicy(), 0, 10]], 
        floorAmount = 10, 
        spawnDistrArgs=[10, DistrType.UNIFORM],
        targetDistrArgs=[10, DistrType.UNIFORM],
        timeDistrArgs = [1, "h", [(1, 1), (1, 1)]],
        spawnEveryArgs = 10) -> None:
        
        self.floorAmount = floorAmount
        self.elevatorArgs = elevatorArgs
        self.spawnDistrArgs= spawnDistrArgs
        self.targetDistrArgs= targetDistrArgs
        self.timeDistrArgs = timeDistrArgs 
        self.spawnEveryArgs = spawnEveryArgs




    def compparative_2d_plotter(self):
        pass

    def comparative_3d_plotter(self):
        pass


    def _setFloorAmount(self,amount:int):
        print("here3")
        self.floorAmount = amount
        self.spawnDistrArgs[0] = amount
        self.timeDistrArgs[0] = amount

        for i in range(len(self.elevatorArgs)):
            self.elevatorArgs[i][1]=amount-1

    def _updateHandler(self, param,newVal,index=0):
        print("here")
        
        match param.case():
            case 0:
                self._updateParam(param,newVal)
            case 1:
                self._updateElevator(param,newVal,index)
            case 2:
                self._updateParamPolicy(param,newVal)
            case 3:
                self._updateTimeDistr(param,newVal)

    def _updateParam(self,param,newVal):
        print("here2")
        match param.value:
            case 1:
                self._setFloorAmount(newVal)
            case 2:
                self.spawnDistrArgs[1] = newVal
            case 3:
                self.targetDistrArgs[1] = newVal
            case 5:
                self.spawnEveryArgs = newVal
        
    def _updateParamPolicy(self,param,Newval):
        pass
        


    def _addElevator(self,args:list):
        amount = len(self.elevatorArgs)
        args[3] = self.elevatorArgs+1
        self.elevatorArgs.append(args)

    def _updateElevator(self,param:ElevatorParameter,newVal,index:int):
        self.elevatorArgs[index][param.value]=newVal

    def _updateSpawnDistr(self,type:DistrType):
        self.spawnDistrArgs[1]= type

    def _updateTargetDistr(self,type:DistrType):
        self.targetDistrArgs[1]= type

    def _updateTimeDistr(self,param:TimeDistrParameter, newVal):
        if (param.value==3):
            self.timeDistrArgs[param.value].append(newVal)
        else:
            self.timeDistrArgs[param.value]=newVal

    def _printArgs(self):
        print("printing args -----")
        print(self.elevatorArgs)
        print(self.floorAmount)
        print(self.spawnDistrArgs)
        print(self.targetDistrArgs)
        print(self.timeDistrArgs)
        print(self.spawnEveryArgs)




