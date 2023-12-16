from debug import Debug as DB

from enum import Enum


class Action(Enum):
    MOVE_DOWN = -2   # Move down
    WAIT_DOWN = -1   # Advertise down: Let passengers enter which want to go down enter
    WAIT = 0        # Doors closed, wait for policy to make a decision
    WAIT_UP = 1      # Advertise up: Let passengers which want to go up enter
    MOVE_UP = 2      # Move up
    WAIT_OPEN = 3    # Advertise no direction: Open doors, let passengers enter/exit no matter the direction


class Policy():
    """
    Base class for all policies, contains the interface for the policy without logic.
    """

    def __init__(self):
        self.prev_action = Action.WAIT
        pass

    def __str__(self) -> str:
        return DB.str(
            "Class",
            "Policy",
            kwargs=[
                self.prev_action],
            desc=["prev_action"])

    def name(self) -> str:
        """To be overwritten by sublcasses"""
        pass

    def get_action(
            self,
            current_floor,
            floor_list,
            elevator_buttons,
            elevators,
            elevator,
            time):
        """
        Returns the action the elevator should take
        """
        floor_buttons = []
        for floor in floor_list:
            floor_buttons.append(floor.button_pressed)

        # Should only be accessed if policy is allowed to see amount of people and where they are going
        # Such policies are marked by "_Enhanced"
        self._floor_list = floor_list

        out = self._decide(
            current_floor,
            floor_buttons,
            elevator_buttons,
            elevators,
            elevator,
            time)

        if (DB.pcy_action_update):
            DB.pr(
                "Func",
                "get_action",
                message="function was called",
                kwargs=[out],
                desc=["action"])
        if ((not DB.pcy_action_update) and DB.pcy_action_update_select and (
                out.value in DB.pcy_action_update_selection)):
            DB.pr(
                "Func",
                "get_action",
                message="function was called",
                kwargs=[out],
                desc=["action"])

        ''' Uncomment if you want to see the state of the simulation at every timestep
        str = f"Elevator {elevator.elevator_index} on \033[93mFloor: {current_floor}\033[0m with {len(elevator.passenger_list)} passengers, pAction: {out}, Target: {elevator.target}, TargetDir: {elevator.target_direction} \n  Floors: ["
        for floor in floor_list:
            suffix = ""
            if len(floor.passenger_list) > 0:
                up = 0
                down = 0
                for p in floor.passenger_list:
                    if (p.end_level > floor.number):
                        up += 1
                    else:
                        down += 1
                cUp = "94m" if up > 0 else "0m"
                cDown = "92m" if down > 0 else "0m"

                suffix = f"\033[{cDown}{down}\033[0m/\033[{cUp}{up}\033[0m"
            else:
                suffix = "0/0"
            str += f"{floor.number}:"+suffix+", "
        print(str[0:-2] + "]")
        '''

        return out

    def _no_elevator_heading(self, elevators, target, target_direction):
        """
        Returns true if another elevator already is going to target with advertised target_direction
        """
        for e in elevators:
            if (e.target == target):
                return False
        return True

    def _has_requests(self, floor_buttons, elevators, elevator_buttons):
        """
        Returns true if there is any passenger waiting and no elevator heading there
        """
        for i, floor in enumerate(floor_buttons):
            if (floor.move_up and self._no_elevator_heading(elevators, i, 1)):
                return True
            elif (floor.move_down and self._no_elevator_heading(elevators, i, -1)):
                return True
        for button in elevator_buttons:
            if (button):
                return True
        return False

    def _has_requests_except_current(
            self,
            floor_buttons,
            elevators,
            elevator_buttons,
            current_floor):
        """
        Returns true if there is any passenger waiting and no elevator heading there
        """
        for i, floor in enumerate(floor_buttons):
            if current_floor == i:
                continue
            if (floor.move_up and self._no_elevator_heading(elevators, i, 1)):
                return True
            elif (floor.move_down and self._no_elevator_heading(elevators, i, -1)):
                return True
        for i, button in enumerate(elevator_buttons):
            if current_floor == i:
                continue
            if (button):
                return True
        return False

    def _decide(
            self,
            current_floor,
            floor_buttons,
            elevator_buttons,
            elevators,
            elevator,
            time):
        """
        Internal implementation of how the policy decides what action to take
        """
        action = Action.WAIT

        # Policy logic goes here

        self.prev_action = action
        return Action.WAIT
