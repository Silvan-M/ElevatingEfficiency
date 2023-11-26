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
    POLICY= 2 
    CAPACITY = 4
    def case(self):
        return 1


class PolicyParameter(Enum):
    ElEVBUTWEIGHT = 0
    FLOORBUTWEIGHT = 1
    DIRWEIGHT = 2
    DISTWEIGHT =  3
    DISTEXPONENT = 4
    TIMEWEIGHT = 5
    def case(self):
        return 2 


class TimeDistrParameter(Enum):
    MAXPASSENGER = 1
    TIMETYPE = 2
    ADDPOINT = 3
    def case(self):
        return 3


    

    



