from elevator import Elevator
from floor import Floor
from passenger import Passenger
from delegate import Delegate
from debug import Debug as DB


class Building():

    def __init__(self, elevators, floor_amount, distribution):
        self.on_passenger_created = Delegate()
        self.elevators = elevators
        self.floor_amount = floor_amount
        self.floors = []
        self.distribution = distribution

        for i in range(floor_amount):
            self.floors.append(Floor(i))

        for i, elevator in enumerate(elevators):
            elevator.set_elevator_index(i)

    def __str__(self) -> str:
        out = DB.str(
            "Class",
            "Building",
            kwargs=[
                self.elevators,
                self.distribution,
                self.floor_amount,
                self.passenger_distribution,
                self.floors],
            desc=[
                "elevators",
                "spawn distribution",
                "target distribution",
                "floor amount",
                "time distribution",
                "floors"])
        return out

    def step(self, time):
        if (DB.bld_fct_step and ((time % int(DB.bld_fct_stepsSkip)) == 0)):
            DB.pr("Func", "step", message="function was called")

        # Spawn new passengers
        if (DB.bld_fct_spawn_passenger and ((time %
                                          int(DB.bld_fct_spawn_passengerStepsSkip)) == 0)):
            DB.pr(
                "Func",
                "spawn_passenger",
                message="function was called",
                t=time)

        spawned_people = self.distribution.get_passengers_to_spawn(time)

        for spawn, target in spawned_people:
            self.spawn_passenger(time, spawn, target)

        for elevator in self.elevators:
            elevator.step(time, self)

    def spawn_passenger(self, time, spawn, target):
        # Create passenger object
        passenger = Passenger(time, spawn, target)

        # Notify listeners
        self.on_passenger_created.notify_all(passenger, time)

        # Add passenger to floor and update floor buttons
        self.floors[spawn].spawn_passenger(passenger, time)

        # Press buttons on floor messages
        if (target > spawn):
            if ((DB.bld_presses_floor_button_up and ((time % int(DB.bld_presses_floor_button_upStepsSkip)) == 0)) or (
                    DB.bld_presses_floor_button and ((time % int(DB.bld_presses_floor_buttonStepsSkip)) == 0))):
                DB.pr(
                    "Func",
                    "spawn_passenger",
                    message="passenger pressed button up",
                    kwargs=[spawn],
                    desc=["floor"],
                    t=time)
        else:
            if ((DB.bld_presses_floor_button_down and ((time % int(DB.bld_presses_floor_button_downStepsSkip)) == 0)) or (
                    DB.bld_presses_floor_button and ((time % int(DB.bld_presses_floor_buttonStepsSkip)) == 0))):
                DB.pr(
                    "Func",
                    "spawn_passenger",
                    message="passenger pressed button down",
                    kwargs=[spawn],
                    desc=["floor"],
                    t=time)
