from policies import Policy
from policies import LOOKPolicy, SCANPolicy, FCFSPolicy, SSTFPolicy, PWDPPolicy, PWDPPolicyEnhanced
from distribution import Distribution, DistrType, TimeDistribution
from debug import Debug as DB
from parameter import Parameter,ElevatorParameter,TimeDistrParameter, PolicyParameter
from exceptions import Exceptions as EXC
from elevator import Elevator
from plotter.plotter2D import Plotter2D as P2D
from building import Building
from simulation import Simulation
from simulation_statistics import Objective

import numpy as np

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
        self.elevatorsInit = [0]*len(elevatorArgs)
        self.floorAmount = floorAmount
        self.spawnDistrArgs= spawnDistrArgs
        self.targetDistrArgs= targetDistrArgs
        self.timeDistrArgs = timeDistrArgs 
        self.spawnEvery = spawnEveryArgs



    def continuous_2d_plotter(self,obj:Objective,param:Parameter,startVal,endVal,steps):
        objectiveData = []
        parameterData = np.linspace(startVal,endVal,num=steps)
        for i in range(len(parameterData)):
            self._updateHandler(param,parameterData[i])
            simulation = self._init()
            simulation.run(minutes=500, timeScale=-1)
            objectiveData.append((round(simulation.statistics.getObjective(obj)),3))
        plt = P2D(parameterData,param.name(),objectiveData,obj.value)
        plt.plotNormal()

    def continuous_2d_plotter_avg(self,trials:int,obj:Objective,param:Parameter,startVal,endVal,steps):
        objectiveData = []
        objectiveTemp=[]
        parameterData = np.linspace(startVal,endVal,num=steps)

    
        for i in range(len(parameterData)):
            for a in range(trials):
                self._updateHandler(param,parameterData[i])
                simulation = self._init()
                simulation.run(minutes=500, timeScale=-1)
                objectiveTemp.append((simulation.statistics.getObjective(obj)))
            
            self._delNone(objectiveTemp)
            objectiveData.append(round(np.mean(objectiveTemp),3))
            objectiveTemp=[]
        plt = P2D(parameterData,param.name(),objectiveData,obj.value)
        plt.plotNormal()
        
        

    def discrete_2d_plotter(self,obj:Objective):
        pass

        

    def continuous_3d_plotter(self):
        pass



    def _init(self):
        spawnDistribution = Distribution(*self.spawnDistrArgs)
        targetDistribution = Distribution(*self.targetDistrArgs)
        timeDistribution = TimeDistribution(*self.timeDistrArgs)
        elevators=[]
        

        for i in range(len(self.elevatorArgs)):
            self._initPolicy(i)
            elevators.append(Elevator(self.elevatorArgs[i][0],self.elevatorArgs[i][1],self.elevatorsInit[i],self.elevatorArgs[i][3]))

        building = Building(elevators,self.floorAmount,spawnDistribution,targetDistribution,timeDistribution,self.spawnEvery)
        return Simulation(building)


    def _initPolicy(self,i):
        t =  type(self.elevatorArgs[i][2][0])
        if (t == LOOKPolicy):
            self.elevatorsInit[i][2] = LOOKPolicy()
        elif (t == LOOKPolicy):
            self.elevatorsInit[i][2] = FCFSPolicy()
        elif (t == SSTFPolicy ):
            self.elevatorsInit[i][2] = SSTFPolicy()
        elif (t == SCANPolicy):
            self.elevatorsInit[i][2] = SCANPolicy()
        elif (t == PWDPPolicy or PWDPPolicyEnhanced):
            args = self.elevatorArgs[i][2][1:]
            self.elevatorsInit[i] = PWDPPolicy(*args)

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
            self.elevatorArgs[index][2][param.value]=newVal

    


    def _addElevator(self,args:list):
        self.elevatorArgs.append(args)
        self.elevatorArgs.append(None)

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
    
    def _delNone(self,lst:list):
        for i in sorted(range(len(lst)),reverse=True):
            if (lst[i]==None):
                lst.pop(i)



x = SimulationPlotter( elevatorArgs=[[0, 9, [PWDPPolicy,1,1,1,1,1,1], 10]])
x.continuous_2d_plotter_avg(100,Objective.AWT,PolicyParameter.DIRWEIGHT,0,5,10)



