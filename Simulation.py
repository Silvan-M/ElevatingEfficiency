from Statistics import Statistics

import time

class Simulation():

    def __init__(self, building):
        self.time = 0
        self.building = building
        self.statistics = Statistics(self)


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
        self.building.step(self.time)
        

        self.time += 1


