from policies.policy import Policy, Action


class SCANPolicy(Policy):
    """
    SCAN Policy
    Move up and down, stop at every floor if someone is waiting
    Change direction if reached top or bottom floor
    """

    def __init__(self):
        self.prev_action = Action.WAIT
        self.going_up = True

    def name(self) -> str:
        return "SCAN Policy"

    def _decide(
            self,
            current_floor,
            floor_buttons,
            elevator_buttons,
            elevators,
            elevator,
            time):
        action = Action.WAIT

        if (not self._has_requests(floor_buttons, elevators, elevator_buttons)):
            # No requests, wait
            action = Action.WAIT_OPEN
        elif (self.going_up):
            # Going up
            if (current_floor == elevator.max_floor):
                # Change direction, since we reached the top floor
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
            if (current_floor == elevator.min_floor):
                # Change direction, since we reached the bottom floor
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
