from debug import Debug as DB

class ButtonPressed():
    def __init__(self):
        self.moveUp = False
        self.moveDown = False
    def __str__(self) -> str:
        return DB.str("Class","ButtonPressed",kwargs=[self.moveDown,self.moveUp],desc=["moveDown","moveUp"])

        

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
