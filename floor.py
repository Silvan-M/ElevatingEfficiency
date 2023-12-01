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
        if (value and self.moveUp == False):
            self.lastPressedUp = time
        else:
            self.lastPressedUp = -1
        self.moveUp = value

    def setMoveDown(self, value, time):
        if (value and self.moveDown == False):
            self.lastPressedDown = time
        else:
            self.lastPressedDown = -1
        self.moveDown = value

    def updateTime(self, direction, time):
        if direction == 1:
            self.lastPressedUp = time
        else:
            self.lastPressedDown = time


class Floor():
    def __init__(self, number):
        self.passengerList = []
        self.buttonPressed = ButtonPressed()
        self.number = number
    
    def __str__(self) -> str:
        return DB.str("Class","Floor",kwargs=[self.passengerList,self.buttonPressed,self.number],desc=["passenger list","buttons pressed","number"])

    def spawnPassenger(self, passenger, time):
        """
        Adds a passenger to the floor and updates the floor buttons
        """
        if (DB.flrPassengerAppended):
            DB.pr("Class","Floor",message="passenger appended")
        self.passengerList.append(passenger)

        # Do not update time since no elevator arrived, only spawn
        self.updateFloorButtons(time, False)

    def removePassenger(self, passenger, time):
        """
        Removes a passenger from the floor and updates the floor buttons
        """
        self.passengerList.remove(passenger)

        # Update Time since elevator arrived
        self.updateFloorButtons(time, True)

    def updateFloorButtons(self, time, updateTime = False):
        """
        Updates the floor buttons based on the passengers on the floor
        """
        up = False
        down = False
        for p in self.passengerList:
            if (p.endLevel > self.number):
                up = True
                self.buttonPressed.updateTime(1, time)
            else:
                down = True
                self.buttonPressed.updateTime(-1, time)

        self.buttonPressed.setMoveUp(up, time)
        self.buttonPressed.setMoveDown(down, time)
        
        if updateTime:
            self.buttonPressed.updateTime(1, time)
            self.buttonPressed.updateTime(-1, time)

