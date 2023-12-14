from policies.policy import Policy, Action


class SSTFPolicy(Policy):
    """
    SSTF Policy (Shortest Seek Time First)
    Move to the closest target in the same direction
    """

    def __init__(self, prefers_elevator_buttons=True):
        self.prev_action = Action.WAIT
        self.going_up = True

        # If true, elevator buttons are preferred over external buttons
        self.prefers_elevator_buttons = prefers_elevator_buttons

    def name(self) -> str:
        return "SSTF Policy"

    def _decide(
            self,
            current_floor,
            floor_buttons,
            elevator_buttons,
            elevators,
            elevator,
            time):
        """
        Choose action based on advertised direction and closest target
        """
        action = Action.WAIT

        if (elevator.target == current_floor or elevator.target == -1):
            # Get new decision if elevator arrived at target or is idle

            # Initilize target
            target, target_direction = -1, 0

            # Get closest target in advertised direction
            if (self._has_requests(floor_buttons, elevators, elevator_buttons)):
                # Has requests, set new target
                target, target_direction = self._get_closest_target(
                    current_floor, floor_buttons, elevator_buttons, elevator.target_direction)

            elevator.target = target
            elevator.target_direction = target_direction

            if (target != -1):
                # New target in different floor, move
                action = Action.WAIT_UP if (
                    target > current_floor) else Action.WAIT_DOWN
            else:
                # No new target or target is current floor, wait
                action = Action.WAIT_OPEN
        elif (self.prev_action in (Action.MOVE_UP, Action.WAIT_UP)):
            # Not reached target yet, continue/start moving up
            action = Action.MOVE_UP
        elif (self.prev_action in (Action.MOVE_DOWN, Action.WAIT_DOWN)):
            # Not reached target yet, continue/start moving down
            action = Action.MOVE_DOWN

        self.prev_action = action
        return action

    def _get_closest_target(
            self,
            current_floor,
            floor_buttons,
            elevator_buttons,
            advertised_direction):
        """
        Get the closest target in the given advertised_direction, returns `[target, target_direction]`
        """
        target = -len(floor_buttons) - 1  # set to invalid, low enough value
        target_direction = 0

        # Check elevator buttons
        for i, button in enumerate(elevator_buttons):
            if (advertised_direction == 1 and i <= current_floor) or (
                    advertised_direction == -1 and i >= current_floor) or i == current_floor:
                # Skip if not in advertised direction or current floor
                continue
            elif (button and abs(i - current_floor) < abs(target - current_floor)):
                target = i

        if (self.prefers_elevator_buttons and target >= 0):
            # If elevator buttons are preferred, return target if found
            return target, 0

        # Check external buttons
        for i, button in enumerate(floor_buttons):
            target_dist = abs(target - current_floor)
            button_dist = abs(i - current_floor)

            if (advertised_direction == 1 and i <= current_floor) or (
                    advertised_direction == -1 and i >= current_floor) or i == current_floor:
                # Skip if not in advertised direction or current floor
                continue
            elif (button.move_up and (button_dist < target_dist)):
                target = i
                target_direction = 1
            elif (button.move_down and (button_dist < target_dist)):
                target = i
                target_direction = -1
            elif ((button.move_up or button.move_down) and (button_dist == target_dist)):
                # If elevator button has same distance as external button,
                # update with target_direction
                target_direction = 1 if button.move_up else -1

        if (target < 0):
            # No target found, set to -1
            target = -1
            target_direction = 0

        return target, target_direction
