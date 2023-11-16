from Debug import Debug as DB

import time

class Simulation():
    time = 0
    building = None

    def __init__(self, building):
        self.building = building

    def __str__(self) -> str:
        return DB.str("Class","Simulation",kwargs=[self.time,self.building],desc=["time","building"])

    def run(self, days=0, hours=0, minutes=0, seconds=0, timeScale = -1):
        stepAmount = (days * 24 * 60 * 60        
                    + hours * 60 * 60 +            
                    + minutes * 60              
                    + seconds)
        
        for i in range(stepAmount):
            self.step()

            if(timeScale > 0):
                time.sleep(timeScale)

    def step(self):
        if (DB.simFctStep and ((self.time % int(DB.simTimeStepsSkip))==0)):
            DB.pr("Func","step",message="function was called",t=self.time)

        self.building.step(self.time)
        

        self.time += 1

        if (DB.simTimeSteps and ((self.time % int(DB.simFctStepSkip))==0)):
            DB.pr("Func","step",kwargs=[self.time],desc=["time incremented to "],t=self.time)
        


