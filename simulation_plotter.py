from policies import Policy
from policies import LOOKPolicy, SCANPolicy, FCFSPolicy, SSTFPolicy, PWDPPolicy, PWDPPolicyEnhanced
from distributions import ShoppingMallDistribution, RooftopBarDistribution, ResidentialBuildingDistribution
from debug import Debug as DB
from parameter import Parameter,ElevatorParameter,TimeDistrParameter, PolicyParameter
from exceptions import Exceptions as EXC
from elevator import Elevator
from plotter.plotter2D import Plotter2D as P2D
from plotter.plotter3D import Plotter3D as P3D
from building import Building
from simulation import Simulation
from simulation_statistics import Objective
from progress_bar import ProgressBar

import numpy as np
import random
import multiprocessing as mp

class SimulationPlotter():
    def __init__(
        self,
        elevatorArgs=[[0, 9, [LOOKPolicy], 10]], 
        distrType=ShoppingMallDistribution,
        seed = -1):
        
        self.distribution = distrType()
        self.floorAmount = self.distribution.floorAmount
        self.seed = seed
        self.elevatorArgs = elevatorArgs
        self.elevatorsInit = []

        for i in range(len(elevatorArgs)):
            self.elevatorsInit.append([])


    def paramPlotter2d(self,obj:list,param:Parameter,startVal,endVal,steps,averageOf=1,savePlot=False, name="paramPlotter2d"):
        """
        Simulate the parameter param with steps amount of simulations equidistant in [startVal,endVal]
        The averageOf defines how often each step stated above gets executed. The average will be taken 
        to further compute any plots. The list obj contains the metrics which will be plotted and measured during 
        this numerical experiment.
        
        """
        objList = obj
        objectiveData = []
        objectiveNames = []
        objectiveTemp = []
        for i in range(len(objList)):
            objectiveNames.append(objList[i].value)
            objectiveData.append([])
            objectiveTemp.append([])
        parameterData = np.linspace(startVal,endVal,num=steps)
        bar = ProgressBar(len(parameterData)*averageOf,"Simulating: ")

    
        for i in range(len(parameterData)):
            self._updateHandler(param,parameterData[i])
            for a in range(averageOf):  
                bar.update()
                simulation = self._init()
                simulation.run(days=1, timeScale=-1)
                for q in range(len(objList)):
                    x = (simulation.statistics.getObjective(objList[q]))
                    objectiveTemp[q].append(x)
            for q in range(len(objList)):
                self._delNone(objectiveTemp[q])
                objectiveData[q].append(np.mean(objectiveTemp[q]))
                objectiveTemp[q]=[]
        plt = P2D(parameterData,param.name(),objectiveData,objectiveNames)
        plt.plotNormal(name,save=savePlot)

        

    def paramPlotter3d(self,obj:Objective,param1:list,param2:list,averageOf=1,savePlot=False,name=""):
        """
        Simulate two parameters param1 and param2 with steps amount of simulations equidistant 
        in their respective [startVal,endVal] The averageOf defines how often each step stated above gets executed. 
        The average will be taken to further compute any plots. The obj represents the metric which will be plotted 
        and measured during this numerical experiment.
        
        """
        objective = obj
        objectiveData = []
        objectiveTemp = []
        par1 = param1[0]
        startVal1 = param1[1]
        endVal1 = param1[2]
        steps1 = param1[3]

        par2 = param2[0]
        startVal2 = param2[1]
        endVal2 = param2[2]
        steps2 = param2[3]

        threads = mp.cpu_count()

        print(f"Plotting {name} with {par1.name()} and {par2.name()} using {threads} threads")

        if (name==""):
            name = self.distribution.distributionName+" Scenario"

        parameterData1 = np.linspace(startVal1,endVal1,num=steps1)
        parameterData2 = np.linspace(startVal2,endVal2,num=steps2)
        bar = ProgressBar(len(parameterData1)*len(parameterData2),"Simulating: ")

    
        pool = mp.Pool()
        results = []

        for i in range(len(parameterData1)):
            for j in range(len(parameterData2)):
                result = pool.apply_async(self._paramPlotter3dWorker, args=(i, j, par1, par2, parameterData1, parameterData2, averageOf, objective, random.randint(0, 1000000)))
                results.append(result)

        objectiveData = []
        for result in results:
            objectiveData.append(result.get())
            bar.update()

        pool.close()
        pool.join()

        objectiveData = [result.get() for result in results]

        print(f"Simulation {name} finished.")

        objectiveData = [result.get() for result in results]
        plt = P3D(parameterData1,par1.name(),parameterData2,par2.name(),objectiveData,objective.value)
        plt.plotNormal(name,showMin=True,showMax=True,save=savePlot,interpolation="bilinear")     

    def _paramPlotter3dWorker(self, i, j, par1, par2, parameterData1, parameterData2, averageOf, objective, seed):
        np.random.seed(seed)
        random.seed(seed)

        objectiveTemp = []
        self._updateHandler(par1, parameterData1[i])
        self._updateHandler(par2, parameterData2[j])
        for a in range(averageOf):  
            simulation = self._init()
            simulation.run(days=1, timeScale=-1)
            x = (simulation.statistics.getObjective(objective))
            objectiveTemp.append(x)
        self._delNone(objectiveTemp)
        return np.mean(objectiveTemp)

    def distrPlotter2d(self,distr,target=False,savePlot=False,name=""):
        distrInit = distr()
        start = 0
        end = distrInit.maxTime
        keyFrames = list(range(start, end + 1))
        floorAmount = self.floorAmount

        if (name==""):
            name = self.distribution.distributionName+" Scenario"

        floorNames = []
        floorTargetData = []
        floorSpawnData = []
        

        for i in range(floorAmount):
            floorNames.append("Floor "+str(i))
            floorTargetData.append([])
            floorSpawnData.append([])


        for t in range(len(keyFrames)):
            floorSpawnDistribution, floorTargetDistribution = distrInit.getFloorDistributions(t)
            for i in range(floorAmount):
                floorTargetData[i].append(floorTargetDistribution.distribution[i])
                floorSpawnData[i].append(floorSpawnDistribution.distribution[i])
        if (target):
            plt = P2D(keyFrames,"time [s]",floorTargetData,floorNames)
        else:
            plt = P2D(keyFrames,"time [s]",floorSpawnData,floorNames)
        plt.plotNormal(name,cmap="viridis",save=savePlot)
    
    def policyPlotter2d(self,objective:Objective,policies:list,timeScale="h",averageOf=1,savePlot=False,name=""):
        bar = ProgressBar(len(policies)*averageOf,"Simulating: ")
        objectiveData = []
        objectiveTemp = []
        objectiveNames = []
        objectiveAverage=[]

        if (timeScale=="h"):
            t = 60*60
        else:
            t = 60

        if (name==""):
            name = self.distribution.distributionName+" Scenario"

        distr = self.distribution
        start = 0
        end = (distr.maxTime)//t
        seedStore = self.seed

        keyFrames = list(range(start, end))

        for i in range(len(policies)):
            self.seed = seedStore
            objectiveNames.append(policies[i].name())
            for j in range(len(self.elevatorArgs)):
                self._updateHandler(PolicyParameter.POLICY,policies[i],j)
            for a in range(averageOf):
                self.seed+=1234  
                bar.update()
                simulation = self._init()
                simulation.run(days=1, timeScale=-1)
                x = (simulation.statistics.getObjective(objective,t,24))
                objectiveTemp.append(x)
            objectiveData.append(self._extractMean(objectiveTemp))
            objectiveTemp=[]
        plt = P2D(keyFrames,"time ["+str(timeScale)+"]",objectiveData,objectiveNames,yLabel=objective.value)
        plt.plotNormal(name,save=savePlot)
        




        
    def _extractMean(self,input:list):
        """
        Extracts the mean of the columns of a matrix represented by input. 
        Individual None values get deleted in a column. When column only consists of 
        None, average will be marked with -1, such that we can handle that case later.
        """
        if (len(input)==0 or input==None):
            raise BaseException("List cannot be empty or of length 0")
        
        avg = []
        avgTemp=[]

        xLen = len(input)
        yLen = len(input[0])
        
        for y in range(yLen):
            for x in range(xLen):
                avgTemp.append(input[x][y])
            self._delNone(avgTemp)
            if (len(avgTemp)==0):
                avgTemp.append(-1)
            avg.append(np.mean(avgTemp))
            avgTemp=[]
        return avg




    def _init(self):
        """
        Initialises an experiment with the current member variables as arguments. 
        The arguments are:
        - elevatorArgs : stores the arguments of the i-th elevator in elevatorArgs[i]
        - distrType : stores the scenario [ShoppingMallDistribution, RooftopBarDistribution, ResidentialBuildingDistribution]
        - self.distribution : stores the distribution
        - self.floorAmount : stores the floor amount
        """
        if (self.seed != -1):
            random.seed(self.seed)
            np.random.seed(self.seed)
        elevators=[]
        for i in range(len(self.elevatorArgs)):
            self._initPolicy(i)
            elevators.append(Elevator(self.elevatorArgs[i][0],self.elevatorArgs[i][1],self.elevatorsInit[i],self.elevatorArgs[i][3]))

        building = Building(elevators,self.floorAmount,self.distribution)
        return Simulation(building)


    def _initPolicy(self,i):
        t =  self.elevatorArgs[i][2][0]
        

        if (t == LOOKPolicy):
            self.elevatorsInit[i] = LOOKPolicy()
        elif (t == FCFSPolicy):
            self.elevatorsInit[i] = FCFSPolicy()
        elif (t == SSTFPolicy ):
            self.elevatorsInit[i] = SSTFPolicy()
        elif (t == SCANPolicy):
            self.elevatorsInit[i] = SCANPolicy()
        elif (t == PWDPPolicy):
            args = self.elevatorArgs[i][2][1:]
            self.elevatorsInit[i] = PWDPPolicy(*args)
        elif (t == PWDPPolicyEnhanced):
            args = self.elevatorArgs[i][2][1:]
            self.elevatorsInit[i] = PWDPPolicyEnhanced(*args)

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

# Choose a seed

seed = -1

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
dist = distribution()
elevatorArgs = [[0, floorAmount-1, [policy,1,1,1,1,1,1], dist.elevatorCapacity]] 

## --- END OF SCENARIO SETTINGS --- ##
if __name__ == "__main__":
    if (seed != -1):
        random.seed(seed)
        np.random.seed(seed)

    if (not isCustomScenario):
        elevatorArgs = []
        # Initilaize distribution to get parameters
        dist = distribution()
        # Standard scenario, set parameters automatically
        floorAmount = dist.floorAmount
        amountOfElevators = dist.amountOfElevators
        for i in range(amountOfElevators):
            elevatorArgs.append([0, floorAmount-1, [policy,1,1,1,1,1,1], dist.elevatorCapacity])
    plt = SimulationPlotter(elevatorArgs=elevatorArgs, distrType=distribution,seed=seed)


    ## --- START OF PLOTTER SETTINGS --- ##

    # IMPORTANT: Keep indentiation of the following lines
    # Call the plotter functions here

    plt.policyPlotter2d(Objective.AWT,[SCANPolicy,PWDPPolicy,FCFSPolicy,PWDPPolicyEnhanced,LOOKPolicy],averageOf=10)
    
    #plt.paramPlotter2d([Objective.AWT],PolicyParameter.DIRWEIGHT,0,5,2,2)

    #plt.paramPlotter3d(Objective.AWT,[PolicyParameter.DIRWEIGHT,0,5,2],[PolicyParameter.DISTWEIGHT,0,5,2],1)





    # plt.distrPlotter2d(distribution,savePlot=True)


    ## --- END OF PLOTTER SETTINGS --- ##