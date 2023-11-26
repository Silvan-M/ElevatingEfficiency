from simulation_statistics import SimulationStatistics
from simulation_statistics import Objective as Objective
from delegate import Delegate
from building import Building
from policies.policy import Policy
from distribution import Distribution,TimeDistribution,DistrType
from elevator import Elevator
from policies.look_policy import LOOKPolicy
from debug import Debug as DB
from color import Colors as C
from exceptions import Exceptions as EXC
from parameter import Parameter
from plotter.comparative_2d_plotter import Comparative_2d_plotter as Plotter2D
from plotter.comparative_3d_plotter import Comparative_3d_plotter as Plotter3D
from enum import Enum
import numpy as np
import time

class SimType(Enum):
    NORMAL=0
    COMPARATIVE2D = 1 # numerical values
    COMPARATIVE3D = 2 # numerical values
    TIMEDISTR = 3     # plot over time
    DISCCOMPARATIVE = 4 # discrete values (i.e. different policies)






class Simulation():

    def __init__(self, building, type: SimType,objective:Objective, kwargs = []):
        '''kwargs = [a,b,c] parameter to change in the following manner
            a = Objective [Enum]
            b = Parameter 1 to change [Enum] (only for comparative 2d plots)
                Linspace Data [start,end,step] for Parameter 1 (only for comparative 2 plots)
            c = Parameter 2 to change [Enum] (only for comparative 3d plots)
                Linspace Data [start,end,step] for Parameter 2 (only for comparative 3d plots)
        '''
        
        EXC.typeChecker("Simulation",
                [building,type,objective],
                [[[[int, int, LOOKPolicy, int, int]],
                int,
                [int, DistrType],
                [int, DistrType],
                [int, str, [tuple, tuple]],
                int],
                SimType,
                Objective])

        self.elevatorsArg = building[0]
        self.floorAmountArg = building[1]
        self.spawnDistrArg = building[2]
        self.targDistrArg = building[3]
        self.timeDistrArg = building[4]
        self.spawnEveryArg = building[5]
        self.building = None
        self.type=type
        self.time = 0
        self.objective = objective
        self.onSimulationStarted = Delegate()
        self.onStepEnd = Delegate()

        if (self.type==SimType.COMPARATIVE2D):
            EXC.typeChecker("Simulation",
                    [building,type,objective,kwargs],
                    [[[[int, int, LOOKPolicy, int, int]],
                    int,
                    [int, DistrType],
                    [int, DistrType],
                    [int, str, [tuple, tuple]],
                    int],
                    SimType,
                    Objective,[[Parameter,float,float,float]]]
                    )
            self.param1 = kwargs[0][0]
            self.param1Start = kwargs[0][1]
            self.param1End = kwargs[0][2]
            self.param1Step = kwargs[0][3]  

        if (self.type==SimType.COMPARATIVE3D):
            EXC.typeChecker("Simulation",
                    [building,type,objective,kwargs],
                    [[[[int, int, LOOKPolicy, int, int]],
                    int,
                    [int, DistrType],
                    [int, DistrType],
                    [int, str, [tuple, tuple]],
                    int],
                    SimType,
                    Objective,[[Parameter,float,float,float],[Parameter,float,float,float]]]
                    )
            self.param1 = kwargs[0][0]
            self.param1Start = kwargs[0][1]
            self.param1End = kwargs[0][2]
            self.param1Step = kwargs[0][3] 
            self.param2 = kwargs[1][0]
            self.param2Start = kwargs[1][1]
            self.param2End = kwargs[1][2]
            self.param2Step = kwargs[1][3] 
        
 


    def __str__(self,level=0) -> str:
        out = DB.str("Class","Simulation",kwargs=[self.time,self.building],desc=["time","building"])
        return out
    
    def createSim(self):
        self.elevator=[]
        for i in range(len(self.elevatorsArg)):
            self.elevator.append(Elevator(*self.elevatorsArg[i]))

        self.spawnDistr = Distribution(*self.spawnDistrArg)
        self.targetDistr = Distribution(*self.targDistrArg)
        self.timeDistr = TimeDistribution(*self.timeDistrArg)

        self.building = Building(self.elevator,self.floorAmountArg,self.spawnDistr,self.targetDistr,self.timeDistr,self.spawnEveryArg)

        self.statistics = SimulationStatistics(self.building)
        self.onSimulationStarted.notify_all(self)




    def run(self, days=0, hours=0, minutes=0, seconds=0, timeScale = -1):
        stepAmount = (days * 24 * 60 * 60        
                    + hours * 60 * 60            
                    + minutes * 60              
                    + seconds)

        if (self.type==SimType.NORMAL):
            self.createSim()
            for i in range(stepAmount):
                self.step()

                if(timeScale > 0):
                    time.sleep(timeScale)
            self.statistics.writeToFile("results.txt")
            print("Average waiting time: " + str(self.statistics.calculateAverageWaitingTime()))

        elif (self.type ==SimType.COMPARATIVE2D):
            self.createSim()

            self.objective_data = []
            self.param_data = []
            self.stepSim = int((self.param1End-self.param1Start)/self.param1Step)
            self.paramVal = int(self.param1Start)

            for j in range(self.stepSim):
                
                for i in range(stepAmount):
                    self.step()
                    if(timeScale > 0):
                        time.sleep(timeScale)

                self.objective_data.append(round((self.statistics.getObjective(self.objective)),3))
                self.param_data.append(self.paramVal)
                self.paramVal =  self.paramVal + self.param1Step
                self.updateParam(self.param1,self.paramVal)

            print(self.objective_data)
            print(self.param_data)
            plt = Plotter2D(self.objective_data,self.param_data,self.objective)
            plt.plotNormal()
        elif (self.type ==SimType.COMPARATIVE3D):
            print("here")
            paramVal1 = np.arange(self.param1Start, self.param1End+self.param1Step, self.param1Step)
            paramVal2 = np.arange(self.param2Start, self.param2End+self.param2Step, self.param2Step)

            self.createSim()
            objective_data = []

            for x in range(len(paramVal1)):
                print("here2")
                objective_data_temp=[]
                for y in range(len(paramVal2)):
                    for i in range(stepAmount):
                        self.step()
                        if(timeScale > 0):
                            time.sleep(timeScale)

                    objective_data_temp.append(round((self.statistics.getObjective(self.objective)),3))
                    self.updateParam(self.param2,paramVal2[y])
                objective_data.append(objective_data_temp)
                self.updateParam(self.param1,paramVal1[x])
            plt = Plotter3D(self.objective,objective_data,paramVal1,paramVal2)
            plt.plotNormal()

                



  


            
    def updateParam(self,param:Parameter,newVal:any):
        paramLoc = param.value

        if (paramLoc[0]==0): ## elevatorParam
            if (paramLoc[1]==0): ## minfloor
                self.elevatorsArg[0][0]=newVal
                pass
            elif (paramLoc[1]==1): ## maxfloor
                self.elevatorsArg[0][1]=newVal
            elif (paramLoc[1]==2): ## policy change
                pass
            elif (paramLoc[1]==3): ## pwdp policy
                self.loc = paramLoc[2]
            elif  (paramLoc[1]==4): ## maxCapacity
                self.elevatorsArg[0][4]=newVal

                
        elif (paramLoc[0]==1): ## FloorAmount
            self.floorAmountArg=newVal
        elif (paramLoc[0]==2): ## SpawnDistr
            self.spawnDistrArg=newVal

        elif (paramLoc[0]==3): ## TargetDistr
            self.targetDistrArg=newVal
        elif (paramLoc[0]==4): ## TimeDistr
            self.timeDistrArg = newVal

        elif (paramLoc[0]==5): ## SpawnEvery
            self.spawnEveryArg=newVal

    def step(self):
        if (DB.simFctStep and ((self.time % int(DB.simTimeStepsSkip))==0)):
            DB.pr("Func","step",message="function was called",t=self.time)

        self.building.step(self.time)
        self.time += 1

        self.onStepEnd.notify_all(self)
        if (DB.simTimeSteps and ((self.time % int(DB.simFctStepSkip))==0)):
            DB.pr("Func","step",kwargs=[self.time],desc=["time incremented to "],t=self.time)
        


