
class ButtonPressed():
    def __init__(self):
        self.moveUp = False
        self.moveDown = False
        

class Floor():
    def __init__(self, number):
        self.passengerList = []
        self.buttonPressed = ButtonPressed()
        self.number = number

    def spawnPassenger(self, passenger):
        self.passengerList.append(passenger)
