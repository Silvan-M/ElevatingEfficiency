from policies import Policy
from policies import LOOKPolicy, SCANPolicy, FCFSPolicy, SSTFPolicy, PWDPPolicy, PWDPPolicyEnhanced
from distribution import Distribution, DistrType, TimeDistribution
from debug import Debug as DB
from parameter import Parameter,ElevatorParameter,TimeDistrParameter, PolicyParameter
from exceptions import Exceptions as EXC

class SimulationPlotter():
    def __init__(
        self,
        elevatorArgs=[[0, 9, [LOOKPolicy], 0, 10]], 
        floorAmount = 10, 
        spawnDistrArgs=[10, DistrType.UNIFORM],
        targetDistrArgs=[10, DistrType.UNIFORM],
        timeDistrArgs = [1, "h", [(1, 1), (1, 1)]],
        spawnEveryArgs = 10) -> None:
        
        
        self.elevatorArgs = elevatorArgs
        self.floorAmount = floorAmount
        self.spawnDistrArgs= spawnDistrArgs
        self.targetDistrArgs= targetDistrArgs
        self.timeDistrArgs = timeDistrArgs 
        self.spawnEveryArgs = spawnEveryArgs



    def compparative_2d_plotter(self):
        pass

    def comparative_3d_plotter(self):
        pass

    def _init(self):
        spawnDistribution = Distribution(*self.spawnDistrArgs)
        targetDistribution = Distribution(*self.targetDistrArgs)
        timeDistribution = TimeDistribution(*self.timeDistrArgs)
        elevators=[]
        

        for i in range(len(self.elevatorArgs)):
            elevators.append(Elevator(*self.elevatorArgs[i]))


    def _initPolicy(self,i):
        match self.elevatorArgs[i][2][0]:
            case LOOKPolicy():
                self.elevatorArgs[i][2] = LOOKPolicy()
            case FCFSPolicy():
                self.elevatorArgs[i][2] = FCFSPolicy()
            case SSTFPolicy():
                self.elevatorArgs[i][2] = SSTFPolicy()
            case SCANPolicy():
                self.elevatorArgs[i][2] = SCANPolicy()
            case PWDPPolicy():
                args = self.elevatorArgs[i][2][1:]
                self.elevatorArgs[i][2] = PWDPPolicy(*args)
            case PWDPPolicyEnhanced():
                args = self.elevatorArgs[i][2][1:]
                self.elevatorArgs[i][2] = PWDPPolicyEnhanced(*args)
            

        



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
                self._updatePolicy(param,newVal,index)
            case 3:
                self._updateTimeDistr(param,newVal)

    def _updateParam(self,param,newVal):
        match param.value:
            case 1:
                self._setFloorAmount(newVal)
            case 2:
                self.spawnDistrArgs[1] = newVal
            case 3:
                self.targetDistrArgs[1] = newVal
            case 5:
                self.spawnEveryArgs = newVal
        
    def _updatePolicy(self,param,newVal,index:int):
        if (param.value==-1):
            self.elevatorArgs[index][2]=[newVal]
        else:
            print(self.elevatorArgs[index][2])
            self.elevatorArgs[index][2][param.value]=newVal

    


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




