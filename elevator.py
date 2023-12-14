from policies import Action
from delegate import Delegate
from debug import Debug as DB

import random


class Elevator:
    def __init__(self, min_floor, max_floor, policy, capacity):
        self.on_passenger_entered = Delegate()
        self.on_passenger_exited = Delegate()

        self.min_floor = min_floor
        self.max_floor = max_floor

        self.current_height = random.randint(min_floor, max_floor) * 100
        self.fps = 10  # floors per second (in Percent)
        self.decision = Action.WAIT
        self.passenger_list = []
        self.policy = policy
        self.elevator_buttons = [False] * (max_floor + 1)
        self.elevator_index = 0
        self.target = -1            # Target floor
        # Direction that will be taken once reached target (-1 = down, 0 =
        # undefined, 1 = up)
        self.target_direction = 0
        self.capacity = capacity

    def __str__(self) -> str:
        return DB.str(
            "Class",
            "Elevator",
            kwargs=[
                self.max_floor,
                self.min_floor,
                self.current_height,
                self.fps,
                self.decision,
                self.passenger_list,
                self.policy,
                self.elevator_buttons],
            desc=[
                "max floor",
                "min floor",
                " current height",
                "fps",
                "decision",
                "passengerlist",
                "policy",
                "buttons pressed"])

    def set_elevator_index(self, index):
        self.elevator_index = index

    def get_current_floor(self):
        return self.current_height // 100

    def get_elevator_index(self):
        return self.elevator_index

    def step(self, time, building):
        self.time = time
        if (DB.elv_fct_step and ((time % int(DB.elv_fct_stepsSkips)) == 0)):
            DB.pr("Func", "step", message="function was called", t=time)

        # Check if we are at a floor, approximate if error occurred
        if (((self.current_height + self.fps / 2) % 100 <= self.fps) and
                (self.decision == Action.MOVE_UP or self.decision == Action.MOVE_DOWN)):
            # Wait for policy to make a decision
            self.current_height = round(self.current_height / 100.0) * 100
            self.decision = Action.WAIT

        current_floor = self.get_current_floor()

        if (self.decision == Action.WAIT):
            # Waiting, get decision from policy
            self.decision = self.policy.get_action(
                current_floor,
                building.floors,
                self.elevator_buttons,
                building.elevators,
                self,
                time)
        elif (self.decision == Action.WAIT_UP or self.decision == Action.WAIT_DOWN or self.decision == Action.WAIT_OPEN):
            # Waiting to go up or down, ask passengers to enter if they go in
            # same direction

            # Check if any passenger wants to leave
            for p in self.passenger_list:
                if (p.end_level == current_floor):
                    if (DB.elv_passenger_leaves_elevator and (
                            (time % int(DB.elv_passenger_leaves_elevatorSkips)) == 0)):
                        DB.pr(
                            "Func",
                            "step",
                            message="passenger left elevator",
                            t=time,
                            kwargs=[p],
                            desc=["passenger"])

                    # Remove passenger from elevator, notify observers (for
                    # statistics)
                    self.passenger_list.remove(p)
                    self.on_passenger_exited.notify_all(p, time)
                    return

            # Since we arrived at floor, disable button
            self.elevator_buttons[current_floor] = False

            # Check if any passenger wants to enter
            floor = building.floors[current_floor]
            for p in floor.passenger_list:
                # Check if passenger wants to go in same direction
                if ((p.end_level < current_floor and self.decision == Action.WAIT_DOWN) or (
                        p.end_level > current_floor and self.decision == Action.WAIT_UP) or Action.WAIT_OPEN) and self.capacity > len(self.passenger_list):
                    # Elevator still has capacity and a passenger wants to
                    # enter, thus passenger leaves floor

                    # Remove passenger and update floor buttons
                    floor.remove_passenger(p, time)

                    if (DB.elv_passenger_enters_elevator and (
                            (time % int(DB.elv_passenger_enters_elevatorSkips)) == 0)):
                        DB.pr(
                            "Func",
                            "step",
                            message="passenger entered elevator",
                            t=time,
                            kwargs=[p],
                            desc=["passenger"])

                    # Add passenger to elevator and press button of passenger
                    # destination
                    self.passenger_list.append(p)
                    self.elevator_buttons[p.end_level] = True

                    if (DB.elv_passenger_pressed_button and (
                            (time % int(DB.elv_passenger_pressed_buttonSkips)) == 0)):
                        DB.pr(
                            "Func",
                            "step",
                            message="passenger pressed button",
                            t=time,
                            kwargs=[
                                p.end_level],
                            desc=["level"])

                    self.on_passenger_entered.notify_all(p, time)

                    # We let only one passenger enter per step, thus return
                    return

            # Now that we let all passengers enter, get new decision from
            # policy
            self.decision = self.policy.get_action(
                current_floor,
                building.floors,
                self.elevator_buttons,
                building.elevators,
                self,
                time)

            if (DB.elv_decision_update and (
                    (time % int(DB.elv_decision_updateSkips)) == 0)):
                DB.pr("Func", "step", message="decision was updated",
                      t=time, kwargs=[self.decision], desc=["decision"])

        # Finally move
        if (self.decision == Action.MOVE_DOWN):
            self.current_height = max(0, self.current_height - self.fps)
        elif (self.decision == Action.MOVE_UP):
            self.current_height = min(
                (self.max_floor) * 100,
                self.current_height + self.fps)

        if (DB.elv_movement_update and ((time % int(DB.elv_movement_updateSkips)) == 0)):
            DB.pr(
                "Func",
                "step",
                message="elevator moved",
                t=time,
                kwargs=[
                    self.current_height],
                desc=["height"])
