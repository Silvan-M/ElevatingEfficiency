from policies.policy import Action
from policies.pwdp_policy import PWDPPolicy


class PWDPPolicyEnhanced(PWDPPolicy):
    """
    **PWDP Policy Enhanced (Enhanced Parameterized Weighted Decision Policy)**

    Similar to PWDP Policy, but this time the elevator knows the direction of the passengers and the amount of passengers
    Policy which evaluates each floor by giving it a score using the input parameters (see below).

    The score for the i-th floor advertising [Up/Down] is calculated as follows (changes are marked with ``x``):

    .. code-block:: python

        s1x = people_in_elevator_button_weight * amount_of_people_in_elevator_going_to_floor(i)
        s2  = elevator_buttons[i] * elevator_button_weight * elevator_button_time_weight * (target_button_time / max(1, max_elevator_button_time))
        s3x = people_floor_weight * amount_of_people_in_floor(i).moving[Up/Down]
        s4  = floor_button_weight * floor_button_time_weight * (max_floor_button_time[i] / max(max_all_floor_button_time, 1))
        s5  = sum(elevator_distances) * competitor_weight
        s6  = distance_weight^(distance_exponent) * abs(current_floor - i)

    
    Additionally ``s3 = 0`` if elevator capacity is reached

    Then the i-th floor advertising [Up/Down] will have score:

    .. code-block:: python

        Score = (s1 + s2 + s3 + s4) / max(1, (s5 + s6))
    
    The elevator will then choose the highest scored floor, set it as target, and move to it.
    Along the way, it will stop at each floor if someone wants to enter or exit the elevator on that floor.

    :param people_in_elevator_button_weight: (changed) Award high amount of people that pressed elevator button for floor i
    :param elevator_button_time_weight: Award elevator buttons which were pressed a long time ago
    :param people_floor_weight: (changed) Award high amount of people waiting on floor i
    :param floor_button_time_weight: Award floor buttons which were pressed a long time ago
    :param competitor_weight: Penalize if other elevators are heading to floor i
    :param distance_weight: Penalize high distance to target
    :param distance_exponent: Exponent for distance penalty
    :type people_in_elevator_button_weight: float
    :type elevator_button_time_weight: float
    :type people_floor_weight: float
    :type floor_button_time_weight: float
    :type competitor_weight: float
    :type distance_weight: float
    :type distance_exponent: float
    """

    def __init__(
            self,
            people_in_elevator_button_weight=1,
            elevator_button_time_weight=1,
            people_floor_weight=1,
            floor_button_time_weight=1,
            competitor_weight=1,
            distance_weight=1,
            distance_exponent=1):
        self.prev_action = Action.WAIT
        self.people_in_elevator_button_weight = people_in_elevator_button_weight
        self.people_floor_weight = people_floor_weight

        super().__init__(
            elevator_button_weight=1,
            elevator_button_time_weight=elevator_button_time_weight,
            floor_button_weight=1,
            floor_button_time_weight=floor_button_time_weight,
            competitor_weight=competitor_weight,
            distance_weight=distance_weight,
            distance_exponent=distance_exponent
        )

    def name(self) -> str:
        return "PWDP Enhanced Policy"

    # Override functions from PWDPPolicy, rest of the logic remains exactly
    # the same

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

        if (elevator.capacity == len(elevator.passenger_list)):
            s3 = 0

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
        Get s1, weighed amount of people in elevator going to target
        """
        # Get amount of people in elevator going to target
        amount = 0
        for p in elevator.passenger_list:
            if (p.end_level == target):
                amount += 1

        return self.people_in_elevator_button_weight * amount

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
        Get s3, weighed amount of people in floor moving
        """
        amount_of_people_in_floor_moving_in_target_dir = len(
            self._floor_list[target].passenger_list)

        return self.people_floor_weight * amount_of_people_in_floor_moving_in_target_dir
