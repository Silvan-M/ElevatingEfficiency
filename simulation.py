from simulation_statistics import SimulationStatistics
from delegate import Delegate
from debug import Debug as DB

import time

class Simulation():

    def __init__(self, building):
        self.time = 0
        self.onSimulationStarted = Delegate()
        self.onStepEnd = Delegate()
        self.onSimulationFinished = Delegate()
        self.building = building
        self.statistics = SimulationStatistics(self)


    def __str__(self,level=0) -> str:
        out = DB.str("Class","Simulation",kwargs=[self.time,self.building],desc=["time","building"])
        return out


    def run(self, days=0, hours=0, minutes=0, seconds=0, timeScale = -1):
        print("hi")
        stepAmount = (days * 24 * 60 * 60        
                    + hours * 60 * 60 +            
                    + minutes * 60              
                    + seconds)
        
        self.onSimulationStarted.notify_all(self, stepAmount)
        for i in range(stepAmount):
            self.step()

            if(timeScale > 0):
                time.sleep(timeScale)

        self.onSimulationFinished.notify_all(self)
        

    def step(self):
        if (DB.simFctStep and ((self.time % int(DB.simTimeStepsSkip))==0)):
            DB.pr("Func","step",message="function was called",t=self.time)

        self.building.step(self.time)
        self.time += 1

        self.onStepEnd.notify_all(self, self.time)
        if (DB.simTimeSteps and ((self.time % int(DB.simFctStepSkip))==0)):
            DB.pr("Func","step",kwargs=[self.time],desc=["time incremented to "],t=self.time)
        