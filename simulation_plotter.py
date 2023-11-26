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
        elevatorArgs=[[0, 9, [LOOKPolicy], 10]], 
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
        self.spawnEvery = spawnEveryArgs



    def comparative_2d_plotter(self):
        simulation = self._init()
        simulation.run(minutes=50, timeScale=-1)
        

    def comparative_3d_plotter(self):
        pass

    def _init(self):
        spawnDistribution = Distribution(*self.spawnDistrArgs)
        targetDistribution = Distribution(*self.targetDistrArgs)
        timeDistribution = TimeDistribution(*self.timeDistrArgs)
        elevators=[]
        

        for i in range(len(self.elevatorArgs)):
            self._initPolicy(i)
            print(self.elevatorArgs[i])
            elevators.append(Elevator(*self.elevatorArgs[i]))

        building = Building(elevators,self.floorAmount,spawnDistribution,targetDistribution,timeDistribution,self.spawnEvery)
        return Simulation(building)


    def _initPolicy(self,i):
        t =  type(self.elevatorArgs[i][2][0])
        if (t == LOOKPolicy):
            self.elevatorArgs[i][2] = LOOKPolicy()
        elif (t == LOOKPolicy):
            self.elevatorArgs[i][2] = FCFSPolicy()
        elif (t == SSTFPolicy ):
            self.elevatorArgs[i][2] = SSTFPolicy()
        elif (t == SCANPolicy):
            self.elevatorArgs[i][2] = SCANPolicy()
        elif (t == PWDPPolicy or PWDPPolicyEnhanced):
            args = self.elevatorArgs[i][2][1:]
            self.elevatorArgs[i][2] = PWDPPolicy(*args)

    def _setFloorAmount(self,amount:int):
        self.floorAmount = amount
        self.spawnDistrArgs[0] = amount
        self.timeDistrArgs[0] = amount

        for i in range(len(self.elevatorArgs)):
            self.elevatorArgs[i][1]=amount-1

    def _updateHandler(self, param,newVal,index=0):
        
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
                self.spawnEvery = newVal
        
    def _updatePolicy(self,param,newVal,index:int):
        if (param.value==-1):
            self.elevatorArgs[index][2]=[newVal]
        else:
            print(self.elevatorArgs[index][2])
            self.elevatorArgs[index][2][param.value]=newVal

    


    def _addElevator(self,args:list):
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
        print(self.spawnEvery)


x = SimulationPlotter()
x.comparative_2d_plotter()



