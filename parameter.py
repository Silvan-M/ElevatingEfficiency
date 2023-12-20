from enum import Enum


class Parameter(Enum):
    """
    Enum to represent the different types of parameters
    """
    FLOOR_AMOUNT = 1
    SPWD_STR_TYPE = 2
    TAR_DSTR_TYPE = 3

    def case(self):
        """
        Returns the type of the parameter
        
        :return: type of the parameter
        :rtype: int
        """
        return 0

    def name(self):
        """
        Returns the name of the parameter
        
        :return: name of the parameter
        :rtype: str
        """
        if (self.value == 1):
            return "amount of floors"
        elif (self.value == 5):
            return "spawn every "


class ElevatorParameter(Enum):
    """
    Represents parameter of type elevator
    """
    MIN_FLOOR = 0
    MAX_FLOOR = 1

    CAPACITY = 3

    def case(self):
        """
        Returns the type of the parameter
        
        :return: type of the parameter
        :rtype: int
        """
        return 1

    def name(self):
        """
        Returns the name of the parameter
        
        :return: name of the parameter
        :rtype: str
        """
        if (self.value == 0):
            return "min floor"
        elif (self.value == 1):
            return "max floor "
        elif (self.value == 3):
            return "capacity"


class PolicyParameter(Enum):
    """
    Represents parameter of type policy
    """
    POLICY = -1
    ELEV_BUT_WEIGHT = 1
    ELEV_BUT_TIME_WEIGHT = 2
    FLOOR_BUT_WEIGHT = 3
    FLOOR_BUT_TIME_WEIGHT = 4
    COMP_WEIGHT = 5
    DIST_WEIGHT = 6
    DIST_EXPONENT = 7

    def name(self):
        """
        Returns the name of the parameter

        :return: name of the parameter
        :rtype: str
        """
        if (self.value == 1):
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

    def short_name(self):
        """
        Returns the short name of the parameter

        :return: short name of the parameter
        :rtype: str
        """
        if (self.value == 1):
            return "ebw"
        elif (self.value == 2):
            return "ebtw"
        elif (self.value == 3):
            return "fbw"
        elif (self.value == 4):
            return "fbtw"
        elif (self.value == 5):
            return "cw"
        elif (self.value == 6):
            return "dw"
        elif (self.value == 7):
            return "dexp"

    def case(self):
        """
        Returns the type of the parameter

        :return: type of the parameter
        :rtype: int
        """
        return 2


class TimeDistrParameter(Enum):
    """
    Represents parameter of type time distribution
    """
    MAX_PASSENGER = 1
    TIME_TYPE = 2
    ADD_POINT = 3

    def case(self):
        """
        Returns the type of the parameter

        :return: type of the parameter
        :rtype: int
        """
        return 3
