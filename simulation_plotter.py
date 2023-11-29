from policies import Policy
from policies import LOOKPolicy, SCANPolicy, FCFSPolicy, SSTFPolicy, PWDPPolicy, PWDPPolicyEnhanced
from distributions import ShoppingMallDistribution, RooftopBarDistribution, ResidentialBuildingDistribution
from debug import Debug as DB
from parameter import Parameter,ElevatorParameter,TimeDistrParameter, PolicyParameter
from exceptions import Exceptions as EXC
from elevator import Elevator
from plotter.plotter2D import Plotter2D as P2D
from building import Building
from simulation import Simulation
from simulation_statistics import Objective
from progress_bar import ProgressBar

import numpy as np

class SimulationPlotter():
    def __init__(
        self,
        elevatorArgs=[[0, 9, [LOOKPolicy], 10]], 
        distrType=ShoppingMallDistribution):
        
        self.distribution = distrType()
        self.floorAmount = self.distribution.floorAmount

        self.elevatorArgs = elevatorArgs
        self.elevatorsInit = [0]*len(elevatorArgs)


    def continuous_2d_plotter(self,obj:list,param:Parameter,startVal,endVal,steps):
        
        objList = obj
        objectiveData = []
        objectiveNames = []
        for i in range(len(objList)):
            objectiveNames.append(objList[i].value)
            objectiveData.append([])
        parameterData = np.linspace(startVal,endVal,num=steps)
        
        for i in range(len(parameterData)):
            self._updateHandler(param,parameterData[i])
            simulation = self._init()
            simulation.run(minutes=500, timeScale=-1)
            for q in range(len(objList)):
                objectiveData[q].append((round(simulation.statistics.getObjective(objList[q]),3)))

        plt = P2D(parameterData,param.name(),objectiveData,objectiveNames)
        plt.plotNormal()

    def continuous_2d_plotter_avg(self,trials:int,obj:list,param:Parameter,startVal,endVal,steps):
        objList = obj
        objectiveData = []
        objectiveNames = []
        objectiveTemp = []
        for i in range(len(objList)):
            objectiveNames.append(objList[i].value)
            objectiveData.append([])
            objectiveTemp.append([])
        parameterData = np.linspace(startVal,endVal,num=steps)
        bar = ProgressBar(len(parameterData)*trials,"Simulating: ")

    
        for i in range(len(parameterData)):
            for a in range(trials):  
                bar.update()
                self._updateHandler(param,parameterData[i])
                simulation = self._init()
                simulation.run(minutes=100, timeScale=-1)
                for q in range(len(objList)):
                    objectiveTemp[q].append((round(simulation.statistics.getObjective(objList[q]),3)))
            for q in range(len(objList)):
                self._delNone(objectiveTemp[q])
                objectiveData[q].append(round(np.mean(objectiveTemp[q]),3))
                objectiveTemp[q]=[]
        plt = P2D(parameterData,param.name(),objectiveData,objectiveNames)
        plt.plotNormal()
        
        

    def discrete_2d_plotter(self,obj:Objective):
        pass

        

    def continuous_3d_plotter(self):
        pass



    def _init(self):
        elevators=[]
        for i in range(len(self.elevatorArgs)):
            self._initPolicy(i)
            elevators.append(Elevator(self.elevatorArgs[i][0],self.elevatorArgs[i][1],self.elevatorsInit[i],self.elevatorArgs[i][3]))

        building = Building(elevators,self.floorAmount,self.distribution)
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

    def _updateDistr(self,distribution):
        self.distribution = distribution()
        self.floorAmount = self.distribution.floorAmount

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
    
    def _delNone(self,lst:list):
        for i in sorted(range(len(lst)),reverse=True):
            if (lst[i]==None):
                lst.pop(i)


## --- START OF SCENARIO SETTINGS --- ##
## MAIN SCENARIO SETTINGS
# Choose whether to use a standard scenario or a custom scenario
isCustomScenario = False

# Select from one of the three standard scenarios (ShoppingMall, Rooftop, Residential)
distribution = ShoppingMallDistribution

# Choose a policy for the elevators
policy = SCANPolicy


## CUSTOM SCENARIO SETTINGS
# Specify floor amount if using a custom scenario
floorAmount = 10

# Specify elevator list if using a custom scenario
elevatorCapacity = 10
elevatorArgs = [] 

## --- END OF SCENARIO SETTINGS --- ##


if (not isCustomScenario):
    # Initilaize distribution to get parameters
    dist = distribution()
    # Standard scenario, set parameters automatically
    floorAmount = dist.floorAmount
    amountOfElevators = dist.amountOfElevators
    for i in range(amountOfElevators):
        elevatorArgs.append([0, floorAmount, [policy,1,1,1,1,1,1], dist.elevatorCapacity])
plt = SimulationPlotter(elevatorArgs=elevatorArgs, distrType=distribution)


## --- START OF PLOTTER SETTINGS --- ##
# Call the plotter functions here

plt.continuous_2d_plotter_avg(100,[Objective.AWT],PolicyParameter.ElEVBUTWEIGHT,0,5,1000)

## --- END OF PLOTTER SETTINGS --- ##