from policies.policy import Policy, Action


class LOOKPolicy(Policy):
    """
    **LOOK Policy**
    
    Move up and down, stop at every floor if someone is waiting
    Change direction if no requests in current direction
    """

    def __init__(self):
        self.prev_action = Action.WAIT
        self.going_up = True

    def name(self) -> str:
        return "LOOK Policy"

    def _decide(
            self,
            current_floor,
            floor_buttons,
            elevator_buttons,
            elevators,
            elevator,
            time):
        action = Action.WAIT

        has_requests_above = self._has_requests_above(
            current_floor, floor_buttons, elevator_buttons, elevator)
        has_requests_below = self._has_requests_below(
            current_floor, floor_buttons, elevator_buttons, elevator)

        if (not self._has_requests(floor_buttons, elevators, elevator_buttons)):
            # No requests, wait
            action = Action.WAIT_OPEN
        elif (self.going_up):
            # Going up
            if ((not has_requests_above)
                    and has_requests_below or current_floor == elevator.max_floor):
                # Change direction, since no requests above
                self.going_up = False
                action = Action.WAIT_DOWN
            elif (self.prev_action == Action.WAIT_UP):
                # Waited on floor, now move up
                action = Action.MOVE_UP
            elif (floor_buttons[current_floor].move_up or elevator_buttons[current_floor]):
                # Wait on floor, since someone wants to go up
                action = Action.WAIT_UP
            else:
                # No one wants to go up, move up
                action = Action.MOVE_UP
        else:
            # Going down
            if ((not has_requests_below)
                    and has_requests_above or current_floor == elevator.min_floor):
                # Change direction, since no requests below
                self.going_up = True
                action = Action.WAIT_UP
            elif (self.prev_action == Action.WAIT_DOWN):
                # Waited on floor, now move down
                action = Action.MOVE_DOWN
            elif (floor_buttons[current_floor].move_down or elevator_buttons[current_floor]):
                # Wait on floor, since someone wants to go down
                action = Action.WAIT_DOWN
            else:
                # No one wants to go down, move down
                action = Action.MOVE_DOWN

        self.prev_action = action
        return action

    def _has_requests_above(
            self,
            current_floor,
            floor_buttons,
            elevator_buttons,
            elevator):
        """
        Returns true if there are requests above the current floor
        """
        for i in range(current_floor + 1, elevator.max_floor + 1):
            if (floor_buttons[i].move_up or floor_buttons[i].move_down or elevator_buttons[i]):
                return True
        return False

    def _has_requests_below(
            self,
            current_floor,
            floor_buttons,
            elevator_buttons,
            elevator):
        """
        Returns true if there are requests below the current floor
        """
        for i in range(elevator.min_floor, current_floor):
            if (floor_buttons[i].move_up or floor_buttons[i].move_down or elevator_buttons[i]):
                return True
        return False
