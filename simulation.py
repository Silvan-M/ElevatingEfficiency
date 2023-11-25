from simulation_statistics import SimulationStatistics
from simulation_statistics import Objective as Objective
from delegate import Delegate
from building import Building
from debug import Debug as DB
from color import Colors as C
from exceptions import Exceptions as EXC

from enum import Enum
import time

class SimType(Enum):
    NORMAL=0
    COMPARATIVE2D = 1 # numerical values
    COMPARATIVE3D = 2 # numerical values
    TIMEDISTR = 3     # plot over time
    DISCCOMPARATIVE = 4 # discrete values (i.e. different policies)

class Parameter(Enum):
    PEOPLEINELEVATORBUTTONWEIGHT = 0
    DIRECTIONWEIGHT = 1
    PEOPLEFLOORWEIGHT = 2       
    DISTANCEWEIGHT = 3
    DISTANCEEXPONENT = 4       
    TIMEWEIGHT = 5




class Simulation():

    def __init__(self, building, type: SimType,objective:Objective, kwargs = []):
        '''kwargs = [a,b,c] parameter to change in the following manner
            a = Objective [Enum]
            b = Parameter 1 to change [Enum] (only for comparative 2d plots)
                Linspace Data [start,end,step] for Parameter 1 (only for comparative 2 plots)
            c = Parameter 2 to change [Enum] (only for comparative 3d plots)
                Linspace Data [start,end,step] for Parameter 2 (only for comparative 3d plots)
        '''
        EXC.typeChecker("Simulation",[building,type,objective],[Building,SimType,Objective])

        self.time = 0
        self.building = building
        self.statistics = SimulationStatistics(self)
        self.onStepEnd = Delegate()
        self.type=type
        self.objective = kwargs[0]

        if (self.type==SimType.COMPARATIVE2D):
            EXC.typeChecker("Simulation",[building,type,objective,kwargs],[Building,SimType,Objective,[[Parameter,float,float,float]]])
            self.param1 = kwargs[0][0]
            self.param1Start = kwargs[0][1]
            self.param1End = kwargs[0][2]
            self.param1Step = kwargs[0][3]  
        

        if (self.type==SimType.COMPARATIVE3D ):
            EXC.typeChecker("Simulation",[building,type,objective,kwargs],[Building,SimType,Objective,[[Parameter,float,float,float],[Parameter,float,float,float]]])
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


    def run(self, days=0, hours=0, minutes=0, seconds=0, timeScale = -1):
        stepAmount = (days * 24 * 60 * 60        
                    + hours * 60 * 60            
                    + minutes * 60              
                    + seconds)

        if (self.type==SimType.NORMAL):
            for i in range(stepAmount):
                self.step()

                if(timeScale > 0):
                    time.sleep(timeScale)
            self.statistics.writeToFile("results.txt")
            self.statistics.clearHistory()
            print("Average waiting time: " + str(self.statistics.calculateAverageWaitingTime()))

        elif (self.type ==SimType.COMPARATIVE2D):
            self.objective_data = []
            

            for i in range(stepAmount):
                self.step()
                if(timeScale > 0):
                    time.sleep(timeScale)




            self.objective_data.append(self.statistics.getObjective(self.objective))
            self.statistics.clearHistory()


            print("test")

    def step(self):
        if (DB.simFctStep and ((self.time % int(DB.simTimeStepsSkip))==0)):
            DB.pr("Func","step",message="function was called",t=self.time)

        self.building.step(self.time)
        self.time += 1

        self.onStepEnd.notify_all(self)
        if (DB.simTimeSteps and ((self.time % int(DB.simFctStepSkip))==0)):
            DB.pr("Func","step",kwargs=[self.time],desc=["time incremented to "],t=self.time)
        


