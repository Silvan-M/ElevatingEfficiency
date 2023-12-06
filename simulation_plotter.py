from policies import Policy
from policies import LOOKPolicy, SCANPolicy, FCFSPolicy, SSTFPolicy, PWDPPolicy, PWDPPolicyEnhanced
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
import distributions

import numpy as np
import random
import multiprocessing as mp
from datetime import datetime



class SimulationPlotter():
    def __init__(
        self,
        elevatorArgs=[[0, 9, [LOOKPolicy], 10]], 
        distrType=distributions.ShoppingMallDistribution,
        seed = -1,
        distrInit = None):
        
        self.distribution = distrType() if (distrInit==None) else distrInit
        self.floorAmount = self.distribution.floorAmount
        self.seed = seed
        self.elevatorArgs = elevatorArgs
        self.elevatorsInit = []

        for i in range(len(elevatorArgs)):
            self.elevatorsInit.append([])

        self.TASKSPERTHREAD = 4






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
        tempRes = []
        objectiveTemp = []
        par1 = param1[0]
        startVal1 = param1[1]
        endVal1 = param1[2]
        steps1 = param1[3]

        par2 = param2[0]
        startVal2 = param2[1]
        endVal2 = param2[2]
        steps2 = param2[3]

        simulations = []

        threads = mp.cpu_count()

        printName = name if name != "" else self.distribution.distributionName+" Scenario"
        print(f"Plotting {printName} with {par1.name()} and {par2.name()} using {threads} threads with {self.TASKSPERTHREAD} simulations per Thread.")

        if (name==""):
            name = self.distribution.distributionName+" Scenario"

        parameterData1 = np.linspace(startVal1,endVal1,num=steps1)
        parameterData2 = np.linspace(startVal2,endVal2,num=steps2)
    
        pool = mp.Pool()
        simulations = []
        results = []
        objectiveData = []
        seedStore = self.seed
        
        for i in range(len(parameterData2)):
            objectiveData.append([])
            for j in range(len(parameterData1)):
                objectiveData[i].append([])
                self.seed = seedStore

                for k in range(len(self.elevatorArgs)):
                    self._updateHandler(par1, parameterData1[j],k)
                    self._updateHandler(par2, parameterData2[i],k)

        
                for a in range(averageOf):  
                    self.seed+=1234
                    simulation = self._init()
                    simulations.append((j,i,simulation))

        tasks  = self._partitionTasks(simulations)

        bar = ProgressBar(len(tasks),"Simulating: ")
        bar.show()

        for i in range(len(tasks)):
            result = pool.apply_async(self._paramPlotter3dWorker,args=(tasks[i],obj))
            results.append(result)

        tempRes = []
      
        for result in results:
            tempRes.append(result.get())
            bar.update()
            
        tempRes =  self._unpartitionResults(tempRes)

        pool.close()
        pool.join()

        print(f"Simulation {name} finished.")

        for i in range(len(tempRes)):
            vari = tempRes[i][0]
            varj = tempRes[i][1]
            objectiveData[varj][vari].append(tempRes[i][2])

        self._extractMean3d(objectiveData)

        plt = P3D(parameterData1,par1.name(),parameterData2,par2.name(),objectiveData,objective.value)
        plt.plotNormal(name,showMin=True,showMax=True,save=savePlot,interpolation="bilinear")     

    def _paramPlotter3dWorker(self, tuples, obj):
        result = []
        for tuple in tuples:
            simulation=tuple[2]
            simulation.run(days=1, timeScale=-1)
            x = (simulation.statistics.getObjective(obj))
            result.append((tuple[0],tuple[1],x))
        return result
    
    def paramPlotter3dPermutations(self, obj:Objective, fromVal:int, toVal:int, steps:int, avgOf=1):
        """
        Plots all permutations of the parameters in PolicyParameter.
        """
        P = PolicyParameter
        parameters = [P.ELEVBUTTIMEWEIGHT, P.ELEVBUTWEIGHT, P.FLOORBUTTIMEWEIGHT, P.FLOORBUTWEIGHT, P.COMPWEIGHT, P.DISTEXPONENT, P.DISTWEIGHT]
        tot = len(parameters)*(len(parameters)-1)//2
        iter = 1
        current_time = datetime.now().strftime("%H_%M_%S")
        distrNameWithoutSpaces = self.distribution.distributionName.replace(" ", "-")
        
        print("Starting to plot all parameter permutations.")

        for i, p1 in enumerate(parameters):
            for j, p2 in enumerate(parameters):
                if (j >= i):
                    continue
                name = f"{p1.shortName()}-vs-{p2.shortName()}-{distrNameWithoutSpaces}-{current_time}"
                print(f"PLOTTING {iter}/{tot}: {name}")
                self.paramPlotter3d(obj,[p1, fromVal, toVal, steps],[p2, fromVal, toVal, steps], avgOf, savePlot=True, name=name)
                iter+=1

        print(f"Finished plotting {tot} permutations.")

    def distrPlotter2d(self,distr,target=False,savePlot=False,name="",combineFloors=None,plotTime=0):
        """
        Plots the distribution of the simulation. The target parameter specifies whether the target or spawn distribution should be plotted.
        Combine floors specifies which floors should be combined, input a list of indices tuples of ranges. 
        If None, all floors will be plotted individually.

        If plotTime=0, only the floor distribution will be plotted.
        If plotTime=1, only the time distribution will be plotted.
        If plotTime=2, both will be plotted.
        """
        distrInit = distr()
        start = 0
        end = distrInit.maxTime
        keyFrames = list(range(start, end + 1))
        floorAmount = self.floorAmount

        if (combineFloors==None):
            combineFloors = [(i,i) for i in range(floorAmount)]

        if (name==""):
            name = self.distribution.distributionName+" Scenario"

        curveNames = []
        floorTargetData = []
        floorSpawnData = []


        for i in range(floorAmount):
            floorTargetData.append([])
            floorSpawnData.append([])

        
        if plotTime==0 or plotTime==2:
            for below, above in combineFloors:
                if below != above:
                    curveNames.append(f"Floor {below}-{above}")
                else:
                    curveNames.append(f"Floor {below}")


        timeData = []

        for t in range(len(keyFrames)):
            floorSpawnDistribution, floorTargetDistribution = distrInit.getFloorDistributions(t)
            timeData.append(distrInit.getPassengerAmount(t))

            for i in range(floorAmount):
                if (plotTime==0):
                    floorTargetData[i].append(floorTargetDistribution.distribution[i])
                    floorSpawnData[i].append(floorSpawnDistribution.distribution[i])
                else:
                    floorTargetData[i].append(floorTargetDistribution.distribution[i]*distrInit.getPassengerAmount(t))
                    floorSpawnData[i].append(floorSpawnDistribution.distribution[i]*distrInit.getPassengerAmount(t))

        
        # Convert to hours
        keyFrames = [x/3600 for x in keyFrames]

        # Combine floors
        combinedFloorTargetData = []
        combinedFloorSpawnData = []

        for i,_ in combineFloors:
            combinedFloorTargetData.append(floorTargetData[i])
            combinedFloorSpawnData.append(floorSpawnData[i])

        if plotTime==1:
            # Plot only time distribution
            plt = P2D(keyFrames,"time [h]",[timeData],["Spawn Amount"])
        elif target:
            plt = P2D(keyFrames,"time [h]",combinedFloorTargetData,curveNames)
        else:
            plt = P2D(keyFrames,"time [h]",combinedFloorSpawnData,curveNames)
        plt.plotNormal(name,cmap="winter",save=savePlot,maxVal=24)
    
    def policyPlotter2d(self,objective:Objective,policies:list,timeScale="h",averageOf=1,savePlot=False,name=""):
        bar = ProgressBar(len(policies)*averageOf,"Simulating: ")
        objectiveData = []
        objectiveTemp = []
        objectiveNames = []
        objectiveAverage=[]

        policyAverageEndResult = []

        t = 1
        if (timeScale=="h"):
            t = 60*60
        elif (timeScale=="m"):
            t = 60

        if (name==""):
            name = self.distribution.distributionName+" Scenario"

        distr = self.distribution
        start = 0
        end = (distr.maxTime)//t
        seedStore = self.seed

        keyFrames = list(range(start, end))

        for i in range(len(policies)):
            policyEndResult = []
            self.seed = seedStore
            objectiveNames.append(policies[i]().name())
            for j in range(len(self.elevatorArgs)):
                self._updateHandler(PolicyParameter.POLICY,policies[i],j)
            for a in range(averageOf):
                self.seed+=1234  
                bar.update()
                simulation = self._init()
                simulation.run(days=1, timeScale=-1)
                x = (simulation.statistics.getObjective(objective,t,24*60*60//t))
                objectiveTemp.append(x)
                y = (simulation.statistics.getObjective(objective))
                policyEndResult.append(y)
            objectiveData.append(self._extractMean(objectiveTemp))
            objectiveTemp=[]
            policyAverageEndResult.append(np.mean(policyEndResult))
        for i in range(len(policies)):
            print(f"Policy {policies[i]().name()} has an average of {policyAverageEndResult[i]} {objective.value} at the end of the simulation")
        plt = P2D(keyFrames,"time ["+str(timeScale)+"]",objectiveData,objectiveNames,yLabel=objective.value)
        plt.plotNormal(name,save=savePlot)
        

    def _partitionTasks(self,input:list):
        tasks = [[]]
        currentThread = 0
        currentAmount = 0
        while(len(input)>0):
            if (currentAmount>=self.TASKSPERTHREAD):
                currentAmount = 0
                currentThread +=1
                tasks.append([])
            else:
                tasks[currentThread].append(input.pop())
                currentAmount +=1
        return tasks

    def _unpartitionResults(self,input:list):
        out = []
        for x in range(len(input)):
            for y in range(len(input[x])):
                out.append(input[x][y])
        return out


        
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
        
    def _extractMean3d(self,input:list):
        """
        TODO
        """
        if (len(input)==0 or input==None):
            raise BaseException("List cannot be empty or of length 0")
          
        for x in range(len(input)):
            for y in range(len(input[x])):
                avgTemp=[]
                for c in range(len(input[x][y])):
                    avgTemp.append(input[x][y])
                self._delNone(avgTemp)
                if (len(avgTemp)==0):
                    avgTemp.append(-1) 
                input[x][y] = np.mean(avgTemp)





    def _init(self):
        """
        Initialises an experiment with the current member variables as arguments. 
        The arguments are:
        - elevatorArgs      : stores the arguments of the i-th elevator in elevatorArgs[i]
        - distrType         : stores the scenario [ShoppingMallDistribution, RooftopBarDistribution, ResidentialBuildingDistribution]
        - self.distribution : stores the distribution
        - self.floorAmount  : stores the floor amount
        """
        if (self.seed != -1):
            random.seed(self.seed)
            np.random.seed(self.seed)
        elevators=[]
        for i in range(len(self.elevatorArgs)):
            self._initPolicy(i)
            elevators.append(Elevator(self.elevatorArgs[i][0],self.elevatorArgs[i][1],self.elevatorsInit[i],self.elevatorArgs[i][3]))

        building = Building(elevators,self.floorAmount,self.distribution)
        return Simulation(building,self.seed)


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

    def _genTuple(self,param:Parameter):
        P = PolicyParameter
        parameters = [P.ELEVBUTTIMEWEIGHT, P.ELEVBUTWEIGHT, P.FLOORBUTTIMEWEIGHT, P.FLOORBUTWEIGHT, P.COMPWEIGHT, P.DISTEXPONENT, P.DISTWEIGHT]

        out = []
        for i in parameters:
            if (i!=param):
                out.append((param,i))
        return out



## --- START OF SCENARIO SETTINGS --- ##
## MAIN SCENARIO SETTINGS

# Choose a seed

seed = 1

# Choose whether to use a standard scenario or a custom scenario
isCustomScenario = False

# Select from one of the three standard scenarios (ShoppingMall, Rooftop, Residential)
distribution = distributions.ShoppingMallDistribution

# Choose a policy for the elevators (might be overwritten by function parameters used later)
policy = PWDPPolicy

# Choose policy parameters (might be overwritten by function parameters used later)
policyParameters = [1,1,1,1,1,1,1]

## CUSTOM SCENARIO SETTINGS
# Specify floor amount if using a CUSTOM scenario
floorAmount = 10

# Specify elevator list if using a CUSTOM scenario
elevatorCapacity = 10
elevatorArgs = [[0, floorAmount-1, [policy,1,1,1,1,1,1,1], elevatorCapacity]] 

## --- END OF SCENARIO SETTINGS --- ##
if __name__ == "__main__":

    if (not isCustomScenario):
        elevatorArgs = []
        # Initilaize distribution to get parameters
        dist = distribution()
        # Standard scenario, set parameters automatically
        floorAmount = dist.floorAmount
        amountOfElevators = dist.amountOfElevators
        for i in range(amountOfElevators):
            elevatorArgs.append([0, floorAmount-1, [policy, *policyParameters], dist.elevatorCapacity])
    plt = SimulationPlotter(elevatorArgs=elevatorArgs, distrType=distribution,seed=seed,distrInit=dist)


    ## --- START OF PLOTTER SETTINGS --- ##

    # IMPORTANT: Keep indentiation of the following lines
    # Call the plotter functions here

    # Policy Comparison
    # plt.policyPlotter2d(Objective.AWT,[SCANPolicy, LOOKPolicy, FCFSPolicy, PWDPPolicy, PWDPPolicyEnhanced],averageOf=10)
    
    # Space/Time Distribution
    plt.distrPlotter2d(distribution, savePlot=True, target=True, plotTime=0, name="Shopping Mall - Target Distribution", combineFloors=[(0,9)])

    # Policy Parameter Comparison
    # plt.paramPlotter3d(Objective.ATTD,[PolicyParameter.ELEVBUTWEIGHT,1,6,5],[PolicyParameter.FLOORBUTWEIGHT,1,6,5],2,savePlot=True)

    # Policy Parameter Permutation Comparison
    # plt.paramPlotter3dPermutations(Objective.AWT, 0, 10, 20, avgOf=5)

    # Multiple Policy Parameter Comparison
    runMultiple = False
    fromVal, toVal, steps = 1, 11, 10
    avgOf = 1
    
    parameters = [
        (PolicyParameter.ELEVBUTWEIGHT, PolicyParameter.FLOORBUTWEIGHT),
        (PolicyParameter.ELEVBUTWEIGHT, PolicyParameter.ELEVBUTTIMEWEIGHT),
        (PolicyParameter.COMPWEIGHT, PolicyParameter.COMPWEIGHT),
        (PolicyParameter.FLOORBUTTIMEWEIGHT, PolicyParameter.FLOORBUTWEIGHT),
    ]
    if runMultiple:
        for p1, p2 in parameters:
            plt.paramPlotter3d(Objective.AWT,[p1, fromVal, toVal, steps],[p2, fromVal, toVal, steps], avgOf,savePlot=True)

    ## --- END OF PLOTTER SETTINGS --- ##