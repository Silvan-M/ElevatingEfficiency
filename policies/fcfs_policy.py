from policies.policy import Policy, Action
from debug import Debug as DB
from color import Colors as C


class FCFSPolicy(Policy):
    """
    **First Come First Serve Policy**
    
    Elevator will (directly) go to the first floor that was requested,
    then then it will go to the closest destination in the same direction and carries out until done.
    """

    def __init__(self):
        self.prev_action = Action.WAIT
        self.future_targets = []  # [[target, direction], ...]]

    def name(self) -> str:
        return "FCFS Policy"

    def _decide(
            self,
            current_floor,
            floor_buttons,
            elevator_buttons,
            elevators,
            elevator,
            time):
        """
        Determine which action the elevator should take
        """
        action = Action.WAIT

        if (self.prev_action in (Action.WAIT_UP,
                                Action.WAIT_DOWN, Action.WAIT_OPEN, Action.WAIT)):
            # Get new decision if elevator leaves a target or is idle
            target, target_direction = -1, 0

            # If has requests get next target
            if (self._has_requests(floor_buttons, elevators, elevator_buttons)):
                target, target_direction = self._set_next_target(
                    floor_buttons, elevator_buttons, elevator, current_floor)

            elevator.target = target
            elevator.target_direction = target_direction

            if (target == current_floor):
                # New target is current floor, open doors
                action = Action.WAIT_OPEN
            elif (target != -1):
                # New target in different floor, move
                action = Action.MOVE_UP if (
                    target > current_floor) else Action.MOVE_DOWN
            else:
                # No new target or target is current floor, wait
                action = Action.WAIT_OPEN

            if ((self.prev_action == Action.WAIT_DOWN and action == Action.MOVE_UP) or (
                    self.prev_action == Action.WAIT_UP and action == Action.MOVE_DOWN)):
                action = Action.WAIT
        elif (elevator.target == current_floor or elevator.target == -1):
            # Was Action.MOVE_UP or Action.MOVE_DOWN, elevator has reached target
            # or is idle, wait up or down
            if (elevator.target_direction == 1):
                # Arrived at target, advertise up
                action = Action.WAIT_UP
            elif (elevator.target_direction == -1):
                # Arrived at target, advertise down
                action = Action.WAIT_DOWN
            else:
                # We arrived at target, but have no further targets, wait
                action = Action.WAIT_OPEN
        elif (self.prev_action == Action.MOVE_UP):
            # Not reached target yet, continue moving up
            action = Action.MOVE_UP
        elif (self.prev_action == Action.MOVE_DOWN):
            # Not reached target yet, continue moving down
            action = Action.MOVE_DOWN

        # Safeguarding - Change direction if error occurred
        if ((action == Action.MOVE_DOWN or action == Action.WAIT_DOWN)
                and current_floor == elevator.min_floor):
            if DB.enable_warnings:
                (C.warning(
                    f"WARNING: Elevator tried {action} from min floor {current_floor}, Target: {elevator.target}"))
            action = Action.MOVE_UP
        elif ((action == Action.MOVE_UP or action == Action.WAIT_UP) and current_floor == elevator.max_floor):
            if DB.enable_warnings:
                (C.warning(
                    f"WARNING: Elevator tried {action} from max floor {current_floor}, Target: {elevator.target}"))
            action = Action.MOVE_DOWN

        # Safeguarding - Print warning if elevator did not follow advertised
        # direction
        if ((self.prev_action == Action.WAIT_DOWN and action == Action.MOVE_UP) or (
                self.prev_action == Action.WAIT_UP and action == Action.MOVE_DOWN)):
            if DB.enable_warnings and elevator.elevator_index == 1:
                print(C.warning(
                    f"WARNING: Elevator did not follow advertised direction, {self.prev_action} -> {action}, time: {elevator.time}"))

        self.prev_action = action
        return action

    def _set_next_target(
            self,
            floor_buttons,
            elevator_buttons,
            elevator,
            current_floor):
        """
        Set next target for elevator, returns `[target, target_direction]`
        """
        target = -1
        target_direction = 0

        # Process newly pressed elevator_buttons
        self._update_future_targets(elevator_buttons, elevator, current_floor)

        # Check if there are still future targets (of passengers in elevator)
        while ((target == -1 or target == current_floor)
               and len(self.future_targets) > 0):
            target, target_direction = self.future_targets[0]
            self.future_targets = self.future_targets[1:]

        if (target != -1 and target != current_floor):
            # Found target, If no future targets left, advertise no direction
            # at arrival
            if (len(self.future_targets) == 0):
                target_direction = 0
        elif (target == -1 or target == current_floor):
            # Did not find target, Check if there are passengers (outside of elevator) waiting
            # Find closest passenger in same direction
            closest_target = -1
            closest_target_direction = 0
            closest_distance = float('inf')
            for i, floor in enumerate(floor_buttons):
                if (abs(current_floor - i) >= closest_distance):
                    continue
                elif (floor.move_up and (target_direction == 1 or target_direction == 0)):
                    closest_target = i
                    closest_target_direction = 1
                    closest_distance = i - current_floor
                elif (floor.move_down and (target_direction == -1 or target_direction == 0)):
                    closest_target = i
                    closest_target_direction = -1
                    closest_distance = current_floor - i
            target = closest_target
            target_direction = closest_target_direction

        self.target = target
        return target, target_direction

    def _check_target(self, target):
        """
        Check if target is already in future_targets
        """
        for t, _ in self.future_targets:
            if (t == target):
                return True
        return False

    def _update_future_targets(self, elevator_buttons, elevator, current_floor):
        """
        Determine new targets for elevator and update future_targets accordingly
        Returns amount of new targets
        """
        new_targets = []
        # Check if passengers with new target are in elevator
        for i, button in enumerate(elevator_buttons):
            if (button and not self._check_target(i)):
                new_targets.append(i)

        # If no new targets, return
        if (not new_targets):
            return 0

        # Add new targets (due to FCFS as last priority) to future_targets
        new_targets.sort()
        last_target = self.future_targets[-1][0] if (
            len(self.future_targets) > 0) else current_floor
        # Prefer up if empty
        last_direction = self.future_targets[-1][1] if (
            len(self.future_targets) > 0) else 1

        # Split array into two parts (above and below last_target)
        first_above = -1
        for i in range(len(new_targets)):
            if (new_targets[i] < last_target):
                continue
            elif (new_targets[i] > last_target):
                first_above = i
                break

        below_targets, above_targets = [], []

        if (first_above == -1):
            # No targets above last_target, add all targets below
            below_targets = new_targets
        else:
            below_targets = new_targets[:first_above]
            above_targets = new_targets[first_above:]

        # Sort below_targets in descending order
        below_targets.reverse()

        # Create pairs of target and direction for future_targets
        below_target_pairs = [[target, -1] for target in below_targets]
        above_target_pairs = [[target, 1] for target in above_targets]

        if (elevator.min_floor in below_targets):
            # If min_floor is in below_targets, change direction of last
            # belowTarget
            below_target_pairs[-1][1] = 1
        elif (elevator.max_floor in above_targets):
            # If max_floor is in above_targets, change direction of last
            # aboveTarget
            above_target_pairs[-1][1] = -1

        if (last_direction == 1):
            # If last direction was up, add above_targets first
            if (below_target_pairs and above_target_pairs):
                # If we have below_targets and above_targets, change direction of
                # last aboveTarget
                above_target_pairs[-1][1] = -1
            elif (below_target_pairs and self.future_targets):
                # If we have below_targets and no above_targets, change direction
                # of last futureTarget (if exists)
                self.future_targets[-1][1] = -1

            self.future_targets += above_target_pairs + below_target_pairs
        else:
            # If last direction was down, add below_targets first
            if (above_target_pairs and below_target_pairs):
                # If we have above_targets and below_targets, change direction of
                # last belowTarget
                below_target_pairs[-1][1] = 1
            elif (above_target_pairs and self.future_targets):
                # If we have above_targets and no below_targets, change direction
                # of last futureTarget (if exists)
                self.future_targets[-1][1] = 1

            self.future_targets += below_target_pairs + above_target_pairs

        return len(new_targets)
