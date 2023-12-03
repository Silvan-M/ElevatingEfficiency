from enum import Enum


class Parameter(Enum):
    FLOORAMOUNT = 1
    SPWDSTRTYPE = 2
    TARDSTRTYPE = 3

    def case(self):
        return 0
    
    def name(self):
        if (self.value==1):
            return "amount of floors"
        elif (self.value == 5):
            return "spawn every "

class ElevatorParameter(Enum):
    MINFLOOR = 0
    MAXFLOOR = 1

    CAPACITY = 3
    def case(self):
        return 1

    def name(self):
        if (self.value==0):
            return "min floor"
        elif (self.value == 1):
            return "max floor "
        elif (self.value == 3):
            return "capacity"

class PolicyParameter(Enum):
    POLICY= -1 
    ELEVBUTWEIGHT = 1
    ELEVBUTTIMEWEIGHT = 2
    FLOORBUTWEIGHT = 3
    FLOORBUTTIMEWEIGHT = 4
    COMPWEIGHT = 5
    DISTWEIGHT =  6
    DISTEXPONENT = 7
   
   
    def name(self):
        if (self.value==1):
            return "elevator button weight"
        elif (self.value == 2):
            return "elevator button time weight"
        elif (self.value == 3):
            return "floor button weight"
        elif (self.value == 4):
            return "floor button time weight"
        elif (self.value == 5):
            return "comparator weight"
        elif (self.value == 6):
            return "distance weight"
        elif (self.value == 7):
            return "distance exponent"


    
    def case(self):
        return 2 

class TimeDistrParameter(Enum):
    MAXPASSENGER = 1
    TIMETYPE = 2
    ADDPOINT = 3
    def case(self):
        return 3


    

    



