from enum import Enum


class Parameter(Enum):
    FLOORAMOUNT = 1
    SPWDSTRTYPE = 2
    TARDSTRTYPE = 3
    SPAWNEVERY = 5

    def case(self):
        return 0

class ElevatorParameter(Enum):
    MINFLOOR = 0
    MAXFLOOR = 1

    CAPACITY = 4
    def case(self):
        return 1


class PolicyParameter(Enum):
    POLICY= -1 
    ElEVBUTWEIGHT = 1
    TIMEWEIGHT = 2
    FLOORBUTWEIGHT = 3
    DIRWEIGHT = 4
    COMPWEIGHT = 5
    DISTWEIGHT =  6
    DISTEXPONENT = 7
    
    def case(self):
        return 2 

class TimeDistrParameter(Enum):
    MAXPASSENGER = 1
    TIMETYPE = 2
    ADDPOINT = 3
    def case(self):
        return 3


    

    



