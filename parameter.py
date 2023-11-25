from enum import Enum



class Parameter(Enum):
    ELEVMINFLOOR = [0,0]
    ELEVMAXFLOOR = [0,1]
    ELEVPOLICY = [0,2] 
    ELEVPOLELBUTWEIGHT = [0,3,0]
    ELEVPOLFLBUTWEIGHT = [0,3,1]
    ELEVPOLDIRWEIGHT = [0,3,2]
    ELEVPOLDISWEIGHT =  [0,3,3]
    ELEVPOLDISEXPONENT = [0,3,4]
    ELEVPOLTIMWEIGHT = [0,3,5]
    ELEVCAPACITY = [0,4]
    FLOORAMOUNT = [1]
    SPWDSTRTYPE = [2]
    TARDSTRTYPE = [3]  
    TIMEDSTR = [4]
    SPAWNEVERY = [5] 

    def getVal(self):
        print(self.value)
    



