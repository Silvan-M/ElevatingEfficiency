
from building import Building
from elevator import Elevator

import pygame
import sys
import os
import random

seed_value = 5  
random.seed(seed_value)

class Sprite(pygame.sprite.Sprite):
    cache = {}

    def __init__(self, image_path, initial_position, sprite_size, color=(255, 255, 255)):
        super().__init__()

        self.image = None
        if (image_path, color) in self.cache:
            self.image = self.cache[(image_path, color)]
        else:
            original_image = pygame.image.load(image_path)
            original_image = pygame.transform.scale(original_image, sprite_size)

            color_multiplier = mul(color, 1.0/255)
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

        # Get the rect for positioning
        self.rect = self.image.get_rect()
        self.rect.topleft = initial_position

 
def add(v1, v2):
    return tuple(a + r for a, r in zip(v1, v2))

def mul(v1, c):
    return tuple(e * c for e in v1)       

class GameDisplay():
    def __init__(self, simulation, scale):
        simulation.onStepEnd.add_listener(self.step)
        building = simulation.building
        self.scale = scale
        self.tileSize = 32
        self.totScale = self.tileSize*self.scale

        self.floorAmount = building.floorAmount
        self.additionalBuildingWidth = 3
        self.buildingMargin = (2,1)
        self.elevatorAmount = len(building.elevators)
        self.buildingWidth = self.elevatorAmount + self.additionalBuildingWidth * 2
        self.screenTileAmount = add(mul(self.buildingMargin, 2), (self.buildingWidth, self.floorAmount))

        pygame.init()

        self.screen = pygame.display.set_mode(mul(self.screenTileAmount, self.totScale))
        pygame.display.set_caption("Elevating efficiency")

        self.passengerClothes = './Sprites/Passenger_Clothes.png'
        self.passengerSkin = './Sprites/Passenger_Skin.png'

        self.elevatorBack = './Sprites/ElevatorBack.png'
        self.elevatorFront = './Sprites/ElevatorFront.png'

        self.roomBack = './Sprites/Room_Back_Filled.png'
        self.backElevator = './Sprites/Room_Back_Elevator.png'
        self.roomBackWindow = './Sprites/Room_Back_Window.png'

        self.frontElevator = './Sprites/Room_Front_Elevator.png'
        self.roomFrontWindow = './Sprites/Room_Front_Window.png'
        self.roomFrontSideL = './Sprites/Room_Front_SideLeft.png'
        self.roomFrontSideR = './Sprites/Room_Front_SideRight.png'

        self.whiteTile = './Sprites/White.png'

        self.allSprites = pygame.sprite.Group()
        self.floorColors = []

        self.backgroundColor = (0, 128, 180)
        self.greyColor = (100, 100, 100)

        #Building
        buildingOffset = mul(self.buildingMargin, self.totScale)
        for y in range(self.floorAmount):
            self.floorColors.append((random.randrange(256), random.randrange(256), random.randrange(256)))

            for x in range(self.buildingWidth):
                spriteBack = self.roomBackWindow
                spriteFront = self.roomFrontWindow
                if x == 0:
                    spriteBack = self.roomBack
                    spriteFront = self.roomFrontSideL
                elif x == self.buildingWidth - 1:
                    spriteBack = self.roomBack
                    spriteFront = self.roomFrontSideR
                elif (x >= self.additionalBuildingWidth and x < self.buildingWidth - self.additionalBuildingWidth):
                    spriteBack = self.backElevator
                    spriteFront = self.frontElevator
                loc = add(buildingOffset, (x * self.totScale, y * self.totScale))
                self.allSprites.add(Sprite(spriteBack, loc, (self.totScale, self.totScale), self.floorColors[y]))
                self.allSprites.add(Sprite(spriteFront, loc, (self.totScale, self.totScale)))

        #Elevators
        self.elevators = {}
        for e in building.elevators:
            back = Sprite(self.backElevator, (0,0), (self.totScale, self.totScale))
            front = Sprite(self.frontElevator, (0,0), (self.totScale, self.totScale))
            self.elevators[e.elevatorIndex] = (back, front)
            self.allSprites.add(back)
            self.allSprites.add(front)

        #Ground
        for y in range(self.buildingMargin[1]):
            for x in range(self.screenTileAmount[0]):
                loc = (x * self.totScale, (self.screenTileAmount[1] - y - 1) * self.totScale)
                self.allSprites.add(Sprite(self.whiteTile, loc, (self.totScale, self.totScale), self.greyColor))

    def getShaftLocation(self, elevatorIndex):
        return self.additionalBuildingWidth + elevatorIndex
            

    def step(self, simulation):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


        self.screen.fill(self.backgroundColor)
        self.allSprites.update()
        self.allSprites.draw(self.screen)

        # Update the display
        pygame.display.flip()

