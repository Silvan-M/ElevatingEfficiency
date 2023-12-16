from debug import Debug as DB


class ButtonPressed():
    def __init__(self):
        self.move_up = False
        self.move_down = False
        self.last_pressed_up = -1
        self.last_pressed_down = -1

    def __str__(self) -> str:
        return DB.str(
            "Class", "ButtonPressed", kwargs=[
                self.move_down, self.move_up], desc=[
                "move_down", "move_up"])

    def set_move_up(self, value, time):
        """
        Set the move up button to the given value and update the last pressed time

        :param value: The value to set the button to
        :type value: bool
        :param time: The current time
        :type time: int
        """
        if (value and not self.move_up):
            self.last_pressed_up = time
        elif (not value):
            self.last_pressed_up = -1
        self.move_up = value

    def set_move_down(self, value, time):
        """
        Set the move down button to the given value and update the last pressed time

        :param value: The value to set the button to
        :type value: bool
        :param time: The current time
        :type time: int
        """
        if (value and not self.move_down):
            self.last_pressed_down = time
        elif (not value):
            self.last_pressed_down = -1
        self.move_down = value

    def update_time(self, direction, time):
        if direction == 1:
            self.last_pressed_up = time
        else:
            self.last_pressed_down = time


class Floor():
    def __init__(self, number):
        self.passenger_list = []
        self.button_pressed = ButtonPressed()
        self.number = number

    def __str__(self) -> str:
        return DB.str(
            "Class", "Floor", kwargs=[
                self.passenger_list, self.button_pressed, self.number], desc=[
                "passenger list", "buttons pressed", "number"])

    def spawn_passenger(self, passenger, time):
        """
        Adds a passenger to the floor and updates the floor buttons

        :param passenger: The passenger to add
        :type passenger: Passenger
        :param time: The current time
        :type time: int
        """
        if (DB.flr_passenger_appended):
            DB.pr("Class", "Floor", message="passenger appended")
        self.passenger_list.append(passenger)

        # Do not update time since no elevator arrived, only spawn
        self.update_floor_buttons(time)

    def remove_passenger(self, passenger, time):
        """
        Removes a passenger from the floor and updates the floor buttons

        :param passenger: The passenger to remove
        :type passenger: Passenger
        :param time: The current time
        :type time: int
        """
        self.passenger_list.remove(passenger)

        # Update Time since elevator arrived
        self.update_floor_buttons(time)

    def update_floor_buttons(self, time):
        """
        Updates the floor buttons based on the passengers on the floor

        :param time: The current time
        :type time: int
        """
        up = False
        down = False
        for p in self.passenger_list:
            if (p.end_level > self.number):
                up = True
            else:
                down = True

        self.button_pressed.set_move_up(up, time)
        self.button_pressed.set_move_down(down, time)
