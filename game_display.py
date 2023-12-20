import pygame
import sys
import os
import random
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable


class Sprite(pygame.sprite.Sprite):
    """
    A single image displayed on the live display

    :param image_path: Path to the image
    :param initial_position: Initial position of the image
    :param sprite_size: Size of the image
    :param color: Color of the image
    :type image_path: str
    :type initial_position: tuple
    :type sprite_size: tuple
    :type color: tuple
    """
    cache = {}

    def __init__(
        self,
        image_path,
        initial_position,
        sprite_size,
        color=(
            255,
            255,
            255)):
        super().__init__()

        self.image = None
        if (image_path, color) in self.cache:
            self.image = self.cache[(image_path, color)]
        else:
            original_image = pygame.image.load(image_path)
            original_image = pygame.transform.scale(
                original_image, sprite_size)

            color_multiplier = mul(color, 1.0 / 255)
            self.image = pygame.Surface(sprite_size, pygame.SRCALPHA)
            for y in range(sprite_size[1]):
                for x in range(sprite_size[0]):
                    original_color = original_image.get_at((x, y))
                    multiplied_color = (
                        int(original_color[0] * color_multiplier[0]),
                        int(original_color[1] * color_multiplier[1]),
                        int(original_color[2] * color_multiplier[2]),
                        original_color[3]
                    )
                    self.image.set_at((x, y), multiplied_color)
            self.cache[(image_path, color)] = self.image

        self.rect = self.image.get_rect()
        self.rect.topleft = initial_position


# Vector operations
def add(v1, v2):
    """
    Adds two vectors

    :param v1: First vector
    :param v2: Second vector
    :type v1: tuple
    :type v2: tuple
    :return: Sum of the two vectors
    :rtype: tuple
    """
    return tuple(a + r for a, r in zip(v1, v2))


def mul(v1, c):
    """
    Multiplies a vector by a scalar

    :param v1: Vector
    :param c: Scalar
    :type v1: tuple
    :type c: float or int
    :return: Resulting vector after multiplication
    :rtype: tuple
    """
    return tuple(e * c for e in v1)


def vround(v1):
    """
    Rounds each component of a vector

    :param v1: Vector
    :type v1: tuple
    :return: Vector with each component rounded
    :rtype: tuple
    """
    return tuple(round(e) for e in v1)


def lerp(v1, v2, a):
    """
    Performs linear interpolation between two vectors

    :param v1: First vector
    :param v2: Second vector
    :param a: The interpolation factor
    :type v1: tuple
    :type v2: tuple
    :type a: float
    :return: Resulting vector after interpolation
    :rtype: tuple
    """
    return tuple(v1 * (1 - a) + v2 * a for v1, v2 in zip(v1, v2))


def format_time(seconds):
    """
    Converts from seconds to a string of minutes and hours

    :param seconds: Time in seconds
    :type seconds: int
    :return: Formatted string of minutes and hours
    :rtype: str
    """
    # Calculate days, hours, minutes, and seconds
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Create a formatted string
    time_string = "{:02.0f}:{:02.0f}".format(hours, minutes)

    return time_string


def get_color_at_time(data, time):
    """
    Given a time of day, returns the skycolor

    :param data: Tuple of time in seconds, color
    :param time: Time of day in seconds
    :type data: tuple
    :type time: int
    :return: Color of the sky
    :rtype: tuple
    """
    # Ensure data is sorted by time
    sorted_data = sorted(data, key=lambda x: x[0])

    # Extract times and colors
    times, colors = zip(*sorted_data)

    # Find the index where time should be inserted to maintain sorted order
    idx = next((i for i, t in enumerate(times) if t >= time), len(times) - 1)

    # Interpolate between the colors at idx-1 and idx based on the relative
    # position of time
    t1, c1 = times[idx - 1], colors[idx - 1]
    t2, c2 = times[idx], colors[idx]

    alpha = (time - t1) / (t2 - t1)

    c1_rgb = mcolors.to_rgb(c1)
    c2_rgb = mcolors.to_rgb(c2)

    interpolated_color = (
        c1_rgb[0] + alpha * (c2_rgb[0] - c1_rgb[0]),
        c1_rgb[1] + alpha * (c2_rgb[1] - c1_rgb[1]),
        c1_rgb[2] + alpha * (c2_rgb[2] - c1_rgb[2]),
    )

    return interpolated_color


class SpriteEntity():
    """
    Wrapper class for two sprites, one in the foreground and one in the background.

    :param front: Path to the front sprite
    :param back: Path to the back sprite
    :param screen_loc: Initial location of the sprite
    :param sprite_size: Size of the sprite
    :param front_color: Color of the front sprite
    :param back_color: Color of the back sprite
    :type front: str
    :type back: str
    :type screen_loc: tuple
    :type sprite_size: tuple
    :type front_color: tuple
    :type back_color: tuple
    """
    def __init__(
        self,
        front,
        back,
        screen_loc,
        sprite_size,
        front_color=(
            255,
            255,
            255),
        back_color=(
            255,
            255,
            255)):
        self.front = Sprite(front, screen_loc, sprite_size, front_color)
        self.back = Sprite(back, screen_loc, sprite_size, back_color)
        self.screen_loc = screen_loc
        self.target_pos = screen_loc

    def update_screen_loc(self, screen_loc):
        """
        Updates the screen location of the sprite

        :param screen_loc: New screen location
        :type screen_loc: tuple
        """
        self.screen_loc = screen_loc
        self.front.rect.topleft = screen_loc
        self.back.rect.topleft = screen_loc


class PassengerInfo():
    """
    Condenses the necessary information needed for the game display of a single passenger.

    :param in_elevator: Whether the passenger is in an elevator
    :param index: Index of the elevator or floor
    :param target: Target floor of the passenger
    :type in_elevator: bool
    :type index: int
    :type target: int
    """
    def __init__(self, in_elevator, index, target):
        self.in_elevator = in_elevator
        self.index = index
        self.target = target

    def equal(self, other):
        """
        Indicates whether two PassengerInfo objects are equal

        :param other: Other PassengerInfo object
        :type other: PassengerInfo
        :return: Whether the two objects are equal
        :rtype: bool
        """
        return self.index == other.index and self.in_elevator == other.in_elevator


class SimulationStepInfo():
    """
    Condenses the necessary information needed for the game display of a single simulation step.

    :param building: Building of the simulation
    :type building: Building
    """

    def __init__(self, building):
        self.passengers = {}
        self.elevator_heights = {}

        for f in building.floors:
            for p in f.passenger_list:
                self.passengers[p.id] = PassengerInfo(
                    False, f.number, p.end_level)

        for e in building.elevators:
            for p in e.passenger_list:
                self.passengers[p.id] = PassengerInfo(
                    True, e.elevator_index, p.end_level)
            self.elevator_heights[e.elevator_index] = e.current_height


class GameDisplay():
    """
    Displays the game

    :param simulation: Simulation to display
    :param scale: Scale of the display
    :param start_paused: Whether the game should start paused
    :type simulation: Simulation
    :type scale: float
    :type start_paused: bool
    """

    def __init__(self, simulation, scale, start_paused=False):
        simulation.on_step_end.add_listener(self.step)
        simulation.on_simulation_started.add_listener(self.start_simulation)
        self.scale = scale
        self.paused = start_paused

    def start_simulation(self, simulation, start_time, step_amount):
        """
        Initializes a new simulation
        
        :param simulation: The simulation object to display
        :param start_time: Time in seconds of the time of day
        :param step_amount: Time in seconds of the duration
        :type simulation: Simulation
        :type start_time: int
        :type step_amount: int
        """

        building = simulation.building
        self.time_step_amount = start_time + step_amount
        self.tile_size = 32
        self.tot_scale = round(self.tile_size * self.scale)

        self.floor_amount = building.floor_amount
        self.additional_building_width = 3
        self.building_margin = (2, 1)
        self.elevator_amount = len(building.elevators)
        self.building_width = self.elevator_amount + self.additional_building_width * 2
        self.screen_tile_amount = add(
            mul(self.building_margin, 2), (self.building_width, self.floor_amount))

        # Initialize pygame
        pygame.init()

        self.screen = pygame.display.set_mode(
            mul(self.screen_tile_amount, self.tot_scale))
        pygame.display.set_caption("Elevating efficiency")

        # Sprite paths
        self.passenger_clothes = './Sprites/Passenger_Clothes.png'
        self.passenger_skin = './Sprites/Passenger_Skin.png'

        self.elevator_back = './Sprites/ElevatorBack.png'
        self.elevator_front = './Sprites/ElevatorFront.png'

        self.room_back = './Sprites/Room_Back_Filled.png'
        self.back_elevator = './Sprites/Room_Back_Filled.png'
        self.room_back_window = './Sprites/Room_Back_Window.png'

        self.front_elevator = './Sprites/Room_Front_Elevator.png'
        self.room_front_window = './Sprites/Room_Front_Window.png'
        self.room_front_side_l = './Sprites/Room_Front_SideLeft.png'
        self.room_front_side_r = './Sprites/Room_Front_SideRight.png'

        self.white_tile = './Sprites/White.png'

        self.all_sprites = pygame.sprite.Group()
        self.floor_colors = []

        self.grey_color = (100, 100, 100)

        # Set building sprites
        building_offset = mul(self.building_margin, self.tot_scale)
        for y in range(self.floor_amount):
            self.floor_colors.append(self.get_floor_color(y, self.floor_amount))

            for x in range(self.building_width):
                sprite_back = self.room_back_window
                sprite_front = self.room_front_window
                if x == 0:
                    sprite_back = self.room_back
                    sprite_front = self.room_front_side_l
                elif x == self.building_width - 1:
                    sprite_back = self.room_back
                    sprite_front = self.room_front_side_r
                elif (x >= self.additional_building_width and x < self.building_width - self.additional_building_width):
                    sprite_back = self.back_elevator
                    sprite_front = self.front_elevator
                loc = add(
                    building_offset,
                    (x * self.tot_scale,
                     y * self.tot_scale))
                self.all_sprites.add(
                    Sprite(
                        sprite_back,
                        loc,
                        (self.tot_scale,
                         self.tot_scale),
                        self.floor_colors[y]))
                self.all_sprites.add(
                    Sprite(
                        sprite_front, loc, (self.tot_scale, self.tot_scale)))

        # Set elevator sprites
        self.elevators = {}
        for e in building.elevators:
            ele = SpriteEntity(
                self.elevator_front, self.elevator_back, (0, 0), (self.tot_scale, self.tot_scale))
            self.elevators[e.elevator_index] = ele
            self.all_sprites.add(ele.back)
            self.all_sprites.add(ele.front)

        # Set ground sprites
        for y in range(self.building_margin[1]):
            for x in range(self.screen_tile_amount[0]):
                loc = (
                    x * self.tot_scale,
                    (self.screen_tile_amount[1] - y - 1) * self.tot_scale)
                self.all_sprites.add(
                    Sprite(
                        self.white_tile,
                        loc,
                        (self.tot_scale,
                         self.tot_scale),
                        self.grey_color))

        self.passengers = {}
        self.step_info = None

    def get_floor_color(self, floor_index, floor_amount):
        """
        Returns the floor color of a given floor

        :param floor_index: Index of the floor
        :param floor_amount: Amount of floors
        :type floor_index: int
        :type floor_amount: int
        :return: Color of the floor
        :rtype: tuple
        """
                
        cmap = plt.get_cmap('bone')
        colors = [cmap(i) for i in np.linspace(0, 1, floor_amount)]
        rgb_color = mcolors.to_rgb(colors[floor_amount - floor_index - 1])
        return tuple(int(val * 255) for val in rgb_color)

    def get_shaft_location(self, elevator_index):
        """
        Returns the x-tile-coordinate of an elevator shaft, given the index of an elevator

        :param elevator_index: Index of the elevator
        :type elevator_index: int
        :return: X-tile-coordinate of the elevator shaft
        :rtype: int
        """
        return self.additional_building_width + elevator_index

    def get_passenger_y_coord(self, passenger_info):
        """
        Returns the absolute y-coordinate of a passenger.

        :param passenger_info: Passenger information
        :type passenger_info: PassengerInfo
        :return: Absolute y-coordinate of the passenger
        :rtype: int
        """

        # Moving inside an elevator
        if (passenger_info.in_elevator):
            return self.elevators[passenger_info.index].screen_loc[1] + \
                (10 * self.scale)
        # Staying on a floor
        else:
            return ((self.floor_amount - 1 - passenger_info.index) +
                    self.building_margin[1]) * self.tot_scale + (11 * self.scale)

    def get_random_passenger_location(self, passenger_info):
        """
        Returns the absolute coordinates of a passenger randomized in a floor or elevator.

        :param passenger_info: Passenger information
        :type passenger_info: PassengerInfo
        :return: Absolute coordinates of the passenger
        :rtype: tuple
        """

        # Moving inside an elevator
        if (passenger_info.in_elevator):
            return ((random.uniform(0.05, .65) +
                     self.get_shaft_location(passenger_info.index) +
                     self.building_margin[0]) *
                    self.tot_scale, self.get_passenger_y_coord(passenger_info))
        # Staying on a floor
        else:
            return mul(
                (random.uniform(
                    0.5,
                    self.building_width - .5) + self.building_margin[0],
                    (self.floor_amount - 1 - passenger_info.index) + self.building_margin[1]),
                self.tot_scale)

    def set_background(self, time):
        """
        Sets the background given the current time of day in seconds.

        :param time: Time of day in seconds
        :type time: int
        """

        colors = [(0, "midnightblue"), (5.5, "cornflowerblue"), (6, "lightsalmon"), (7, "skyblue"),
                  (12, "lightskyblue"), (18, "powderblue"), (18.5, "orangered"), (19, "navy"), (24, "midnightblue")]
        hour = (time / 60 / 60) % 24
        col = mul(get_color_at_time(colors, hour), 255)
        grey = (128, 128, 128)
        alpha = .4
        interpolated_color = (
            col[0] + alpha * (grey[0] - col[0]),
            col[1] + alpha * (grey[1] - col[1]),
            col[2] + alpha * (grey[2] - col[2]),
        )
        self.screen.fill(interpolated_color)

    def apply_differences(self, step_info, last_step_info):
        """
        Given two simulation steps, calculate the differences between them:
        
        * Change in elevator location and state
        * Spawning of new passenger
        * Removal of passenger
        * Passenger switched from floor to elevator

        :param step_info: Current simulation step
        :param last_step_info: Previous simulation step
        :type step_info: SimulationStepInfo
        :type last_step_info: SimulationStepInfo
        """

        # Elevator location and state
        for key in step_info.elevator_heights:
            val = step_info.elevator_heights[key]
            elevator = self.elevators[key]
            elevator.update_screen_loc(mul(
                (self.get_shaft_location(key) + self.building_margin[0],
                 (self.floor_amount - 1 - val / 100) + self.building_margin[1]),
                self.tot_scale))

            # Did not move this turn, open door
            if (val == last_step_info.elevator_heights[key]):
                elevator.back.rect.topleft = (-50, -50)

        for key in step_info.passengers:
            val = step_info.passengers[key]

            # Spawn new passenger
            if (key not in self.passengers):  
                loc = self.get_random_passenger_location(val)
                pas = SpriteEntity(self.passenger_clothes, self.passenger_skin, loc, vround(
                    mul((10, 19), self.scale)), self.floor_colors[self.floor_amount - 1 - val.target])
                self.passengers[key] = pas
                self.all_sprites.add(pas.back)
                self.all_sprites.add(pas.front)

            # Switched floor
            elif not val.equal(last_step_info.passengers[key]):  
                loc = self.get_random_passenger_location(val)
                self.passengers[key].update_screen_loc(loc)

            # Height update
            else:  
                p = self.passengers[key]
                loc = (p.screen_loc[0], self.get_passenger_y_coord(val))
                p.update_screen_loc(loc)

        for key in last_step_info.passengers:
            # Passenger removed
            if key not in step_info.passengers:  
                val = self.passengers[key]
                self.all_sprites.remove(val.front)
                self.all_sprites.remove(val.back)

    def render_text(self, txt, loc, alignment=0):
        """
        Renders text to screen
        
        :param txt: String of content to display
        :param loc: Absolute display location to display
        :param alignement: {-1: Left, 0: Center, 1: Right} 
        :type txt: str
        :type loc: tuple
        :type alignment: int
        """
        font = pygame.font.Font(None, round(24 * self.scale))
        text_surface = font.render(txt, True, (255, 255, 255))
        text_rect = text_surface.get_rect()

        if alignment == 0:
            text_rect.center = loc
        elif alignment == 1:
            text_rect.right = loc[0]
            text_rect.centery = loc[1]
        else:
            text_rect.left = loc[0]
            text_rect.centery = loc[1]

        self.screen.blit(text_surface, text_rect)

    def pause_button_pressed(self):
        """
        Check whether the pause button has been pressed

        :return: Whether the pause button has been pressed
        :rtype: bool
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return True
        return False

    def step(self, simulation, time):
        """
        A single frame update of the game display

        :param simulation: Simulation to display
        :param time: Current time of day in seconds
        :type simulation: Simulation
        :type time: int
        """

        # Pause
        self.paused = self.paused or self.pause_button_pressed()

        if self.paused:
            self.render_text("Game Paused", (16 *
                                             self.scale, self.screen_tile_amount[1] *
                                             self.tot_scale -
                                             16 *
                                             self.scale), -
                             1)
            pygame.display.flip()

        while self.paused:
            if self.pause_button_pressed():
                self.paused = False
                break

        # Building step info
        building = simulation.building
        last_step_info = self.step_info
        self.step_info = SimulationStepInfo(building)
        if last_step_info is not None:
            self.apply_differences(self.step_info, last_step_info)

        # Sprites
        self.set_background(simulation.time)
        self.all_sprites.update()
        self.all_sprites.draw(self.screen)

        # Text
        for f in building.floors:
            y_coor = ((self.floor_amount - 1 - f.number) +
                      self.building_margin[1]) * self.tot_scale + 16 * self.scale
            self.render_text(str(len(f.passenger_list)), (-16 * self.scale +
                            self.building_margin[0] * self.tot_scale, y_coor))

        for e in building.elevators:
            self.render_text(str(len(e.passenger_list)), ((self.get_shaft_location(e.elevator_index) +
                                                          self.building_margin[0]) *
                                                         self.tot_scale +
                                                         16 *
                                                         self.scale, self.screen_tile_amount[1] *
                                                         self.tot_scale -
                                                         16 *
                                                         self.scale))

        # Time display
        self.render_text(
            f"{format_time(simulation.time)}",
            (self.screen_tile_amount[0] *
             self.tot_scale -
             16 *
             self.scale,
             16 *
             self.scale),
            1)

        # Name display
        self.render_text(building.distribution.distribution_name,
                        (16 * self.scale, 16 * self.scale), -1)

        # Update the display
        pygame.display.flip()
