from debug import Debug as DB

class ButtonPressed():
    def __init__(self):
        self.moveUp = False
        self.moveDown = False
        self.lastPressedUp = -1
        self.lastPressedDown = -1

    def __str__(self) -> str:
        return DB.str("Class","ButtonPressed",kwargs=[self.moveDown,self.moveUp],desc=["moveDown","moveUp"])
    
    def setMoveUp(self, value, time):
        self.moveUp = value
        if (value):
            self.lastPressedUp = time
        else:
            self.lastPressedUp = -1

    def setMoveDown(self, value, time):
        self.moveDown = value
        if (value):
            self.lastPressedDown = time
        else:
            self.lastPressedDown = -1


class Floor():
    def __init__(self, number):
        self.passengerList = []
        self.buttonPressed = ButtonPressed()
        self.number = number
    
    def __str__(self) -> str:
        return DB.str("Class","Floor",kwargs=[self.passengerList,self.buttonPressed,self.number],desc=["passenger list","buttons pressed","number"])

    def spawnPassenger(self, passenger):
        if (DB.flrPassengerAppended):
            DB.pr("Class","Floor",message="passenger appended")
        self.passengerList.append(passenger)
