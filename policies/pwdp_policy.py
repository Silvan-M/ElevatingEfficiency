from policies.policy import Policy, Action


class PWDPPolicy(Policy):
    """
    **PWDP Policy (Parameterized Weighted Decision Policy)**
    
    Policy which evaluates each floor by giving it a score using input parameters (see below).
    
    The score for the i-th floor advertising [Up/Down] is calculated as follows:
    
    .. code-block:: python

        s1 = elevator_button_weight * elevator_buttons[i]
        s2 = elevator_buttons[i] * elevator_button_weight * elevator_button_time_weight * (target_button_time / max(1, max_elevator_button_time))
        s3 = floor_button_weight * button_pressed
        s4 = floor_button_weight * floor_button_time_weight * (max_floor_button_time[i] / max(max_all_floor_button_time, 1))
        s5 = sum(elevator_distances) * competitor_weight
        s6 = distance_weight^(distance_exponent) * abs(current_floor - i)

    .. code-block:: python
        
        Score = (s1 + s2 + s3 + s4) / max(1, (s5 + s6))

    The elevator will then choose the highest scored floor, set it as target, and move to it.
    Along the way, it will stop at each floor if someone wants to enter or exit the elevator on that floor.

    :param elevator_button_weight: Award elevator button pressed on floor i.
    :param elevator_button_time_weight: Award elevator buttons which were pressed a long time ago.
    :param floor_button_weight: Award floor buttons which were pressed.
    :param floor_button_time_weight: Award floor buttons which were pressed a long time ago.
    :param competitor_weight: Penalize if other elevators are heading to floor i.
    :param distance_weight: Penalize high distance to target.
    :param distance_exponent: Exponent for distance penalty.
    """

    def __init__(
            self,
            elevator_button_weight=1,
            elevator_button_time_weight=1,
            floor_button_weight=1,
            floor_button_time_weight=1,
            competitor_weight=1,
            distance_weight=1,
            distance_exponent=1):
        self.prev_action = Action.WAIT
        self.elevator_button_weight = elevator_button_weight
        self.elevator_button_time_weight = elevator_button_time_weight
        self.floor_button_weight = floor_button_weight
        self.floor_button_time_weight = floor_button_time_weight
        self.competitor_weight = competitor_weight
        self.distance_weight = distance_weight
        self.distance_exponent = distance_exponent
        self.elevatorButtonLastPressed = None

    def name(self) -> str:
        return "PWDP Policy"

    def _decide(
            self,
            current_floor,
            floor_buttons,
            elevator_buttons,
            elevators,
            elevator,
            time):
        """
        Choose action based on floor scores
        """
        action = Action.WAIT

        # Update last pressed elevator button times
        self._update_last_pressed_time(elevator_buttons, time)

        if (self.prev_action in (Action.WAIT_OPEN, Action.WAIT)):
            # Get new decision if elevator leaves a target or is idle
            action = self._get_new_action(
                current_floor,
                floor_buttons,
                elevator_buttons,
                elevators,
                elevator,
                time)
        elif (self.prev_action in (Action.WAIT_UP, Action.WAIT_DOWN)):
            # All passengers entered, close doors and move
            action = Action.MOVE_UP if (
                self.prev_action == Action.WAIT_UP) else Action.MOVE_DOWN
        elif (elevator.target == current_floor or elevator.target == -1):
            # Elevator has reached target or is idle, get new target
            action = self._get_new_action(
                current_floor,
                floor_buttons,
                elevator_buttons,
                elevators,
                elevator,
                time)
        elif (self.prev_action == Action.MOVE_UP):
            # Not reached target yet, continue moving up
            action = Action.WAIT_UP if (
                floor_buttons[current_floor].move_up or elevator_buttons[current_floor]) else Action.MOVE_UP
        elif (self.prev_action == Action.MOVE_DOWN):
            # Not reached target yet, continue moving down
            action = Action.WAIT_DOWN if (
                floor_buttons[current_floor].move_down or elevator_buttons[current_floor]) else Action.MOVE_DOWN

        self.prev_action = action
        return action

    def _get_new_action(
            self,
            current_floor,
            floor_buttons,
            elevator_buttons,
            elevators,
            elevator,
            time):
        """
        Get the new target floor for the elevator
        """
        target = -1

        # Get closest target in advertised direction
        if self._has_requests_except_current(
                floor_buttons,
                elevators,
                elevator_buttons,
                current_floor):
            # There are requests, get highest scored target
            target = self._get_highest_scored_target(
                current_floor, floor_buttons, elevator, elevators, elevator_buttons, time)

        elevator.target = target

        if (target != -1):
            # New target in different floor, move
            action = Action.WAIT_UP if (
                target > current_floor) else Action.WAIT_DOWN
        else:
            # No new target or target is current floor, wait
            action = Action.WAIT_OPEN

        return action

    def _update_last_pressed_time(self, elevator_buttons, time):
        """
        Update last pressed elevator button times
        """
        self.time = time
        if (self.elevatorButtonLastPressed is None):
            # Initialize elevatorButtonLastPressed
            self.elevatorButtonLastPressed = [-1] * len(elevator_buttons)
            self.elevator_button_max_time = 0

        for i in range(len(elevator_buttons)):
            if (elevator_buttons[i]
                    and self.elevatorButtonLastPressed[i] == -1):
                self.elevatorButtonLastPressed[i] = time
            elif (not elevator_buttons[i]):
                self.elevatorButtonLastPressed[i] = -1

    def _get_highest_scored_target(
            self,
            current_floor,
            floor_buttons,
            elevator,
            elevators,
            elevator_buttons,
            time):
        """
        Get the highest scored `[target, target_direction]` in the advertised direction, returns `[target, target_direction]`
        """
        # Get all scores for each target
        scores = self._get_scores(
            current_floor,
            floor_buttons,
            elevator,
            elevators,
            elevator_buttons,
            time)

        # Get highest score
        highest_score_index, _ = max(enumerate(scores), key=lambda x: x[1])

        return highest_score_index

    def _get_scores(
            self,
            current_floor,
            floor_buttons,
            elevator,
            elevators,
            elevator_buttons,
            time):
        """
        Get all scores for each target and target_direction, returns `[(target, target_direction, score)]`
        """
        scores = []

        # Get all scores for each target and target_direction
        for target in range(len(floor_buttons)):
            if (target == current_floor):
                # Do not allow to go to current floor
                scores.append(0)
                continue

            score = self._get_score(
                current_floor,
                floor_buttons,
                elevator,
                elevators,
                elevator_buttons,
                target,
                time)
            scores.append(score)

        return scores

    def _get_score(
            self,
            current_floor,
            floor_buttons,
            elevator,
            elevators,
            elevator_buttons,
            target,
            time):
        """
        Get score for target and target_direction
        """
        # Calculate score and firstly get s1, s2, s3, s4, s5, s6
        s1 = self._get_s1(
            current_floor,
            floor_buttons,
            elevator,
            elevators,
            elevator_buttons,
            target,
            time)
        s2 = self._get_s2(
            current_floor,
            floor_buttons,
            elevator,
            elevators,
            elevator_buttons,
            target,
            time)
        s3 = self._get_s3(
            current_floor,
            floor_buttons,
            elevator,
            elevators,
            elevator_buttons,
            target,
            time)
        s4 = self._get_s4(
            current_floor,
            floor_buttons,
            elevator,
            elevators,
            elevator_buttons,
            target,
            time)
        s5 = self._get_s5(
            current_floor,
            floor_buttons,
            elevator,
            elevators,
            elevator_buttons,
            target,
            time)
        s6 = self._get_s6(
            current_floor,
            floor_buttons,
            elevator,
            elevators,
            elevator_buttons,
            target,
            time)

        return (s1 + s2 + s3 + s4) / max(1, (s5 + s6))

    def _get_s1(
            self,
            current_floor,
            floor_buttons,
            elevator,
            elevators,
            elevator_buttons,
            target,
            time):
        """
        Get s1, weighted elevator button at target
        """
        return self.elevator_button_weight * elevator_buttons[target]

    def _get_s2(
            self,
            current_floor,
            floor_buttons,
            elevator,
            elevators,
            elevator_buttons,
            target,
            time):
        """
        Get s2, weighted time since elevator button of target was pressed
        """
        # Calculate the time since each elevator button was last pressed
        elevatorButtonTimes = (
            abs(
                time -
                self.elevatorButtonLastPressed[i]) for i,
            button in enumerate(elevator_buttons) if button)

        # Get the maximum time, or 1 if no buttons have been pressed
        maxElevatorButtonTime = max(elevatorButtonTimes, default=1)

        targetButtonTime = abs(time - self.elevatorButtonLastPressed[target])

        return 0 if not elevator_buttons[target] else self.elevator_button_weight * \
            self.elevator_button_time_weight * (targetButtonTime / max(1, maxElevatorButtonTime))

    def _get_s3(
            self,
            current_floor,
            floor_buttons,
            elevator,
            elevators,
            elevator_buttons,
            target,
            time):
        """
        Get s3, weighted floor button at target
        """
        button_pressed = floor_buttons[target].move_up or floor_buttons[target].move_down

        return self.floor_button_weight * button_pressed

    def _get_s4(
            self,
            current_floor,
            floor_buttons,
            elevator,
            elevators,
            elevator_buttons,
            target,
            time):
        """
        Get s4, weighted time since floor button of target was pressed
        """
        # Calculate the time since each elevator button was last pressed up
        floorButtonUpTimes = (abs(time - button.last_pressed_up)
                              for button in floor_buttons if button.move_up)

        # Get the maximum time, or 0 if no buttons have been pressed up
        max_floorButtonUpTime = max(floorButtonUpTimes, default=1)

        # Calculate the time since each elevator button was last pressed down
        floorButtonDownTimes = (abs(time - button.last_pressed_down)
                                for button in floor_buttons if button.move_down)

        # Get the maximum time, or 0 if no buttons have been pressed down
        max_floorButtonDownTime = max(floorButtonDownTimes, default=1)

        # Get the target button
        targetButton = floor_buttons[target]

        # Calculate the time since the button was last pressed up, or 0 if it
        # hasn't been pressed up
        timeSinceLastUp = abs(
            time - targetButton.last_pressed_up) if targetButton.move_up else 0

        # Calculate the time since the button was last pressed down, or 0 if it
        # hasn't been pressed down
        timeSinceLastDown = abs(
            time - targetButton.last_pressed_down) if targetButton.move_down else 0

        # Calculate the maximum of the two times
        maxTargetFloorButtonTime = max(timeSinceLastUp, timeSinceLastDown)

        return self.floor_button_weight * self.floor_button_time_weight * \
            (maxTargetFloorButtonTime / max(max_floorButtonUpTime, max_floorButtonDownTime, 1))

    def _get_s5(
            self,
            current_floor,
            floor_buttons,
            elevator,
            elevators,
            elevator_buttons,
            target,
            time):
        """
        Get s5, weighted amount of elevators moving in target_direction (in the view of target)
        """
        # Calculate the distance from each elevator to the current floor,
        # excluding the current elevator
        elevator_distances = [len(elevator_buttons) - abs(e.target - target)
                             for e in elevators if e != elevator]

        return sum(elevator_distances) * self.competitor_weight

    def _get_s6(
            self,
            current_floor,
            floor_buttons,
            elevator,
            elevators,
            elevator_buttons,
            target,
            time):
        """
        Get s6, weighted distance to target
        """
        return abs(current_floor - target) * \
            self.distance_weight ** (self.distance_exponent)
