from enum import Enum


class Parameter(Enum):
    FLOOR_AMOUNT = 1
    SPWD_STR_TYPE = 2
    TAR_DSTR_TYPE = 3

    def case(self):
        return 0

    def name(self):
        if (self.value == 1):
            return "amount of floors"
        elif (self.value == 5):
            return "spawn every "


class ElevatorParameter(Enum):
    MIN_FLOOR = 0
    MAX_FLOOR = 1

    CAPACITY = 3

    def case(self):
        return 1

    def name(self):
        if (self.value == 0):
            return "min floor"
        elif (self.value == 1):
            return "max floor "
        elif (self.value == 3):
            return "capacity"


class PolicyParameter(Enum):
    POLICY = -1
    ELEV_BUT_WEIGHT = 1
    ELEV_BUT_TIME_WEIGHT = 2
    FLOOR_BUT_WEIGHT = 3
    FLOOR_BUT_TIME_WEIGHT = 4
    COMP_WEIGHT = 5
    DIST_WEIGHT = 6
    DIST_EXPONENT = 7

    def name(self):
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
        return 2


class TimeDistrParameter(Enum):
    MAX_PASSENGER = 1
    TIME_TYPE = 2
    ADD_POINT = 3

    def case(self):
        return 3
