
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

        self.rect = self.image.get_rect()
        self.rect.topleft = initial_position


#Vector operations
def add(v1, v2):
    return tuple(a + r for a, r in zip(v1, v2))

def mul(v1, c):
    return tuple(e * c for e in v1)       

class SpriteEntity():
    def __init__(self, front, back, screenLoc, spriteSize, front_color=(255, 255, 255), back_color=(255, 255, 255)):
        self.front = Sprite(front, screenLoc, spriteSize, front_color)
        self.back = Sprite(back, screenLoc, spriteSize, back_color)
        self.screenLoc = screenLoc
        self.targetPos = screenLoc

    def updateScreenLoc(self, screenLoc):
        self.screenLoc = screenLoc
        self.front.rect.topleft = screenLoc
        self.back.rect.topleft = screenLoc


class PassengerInfo():
    def __init__(self, inElevator, index):
        self.inElevator = inElevator
        self.index = index

    def equal(self, other):
        return self.index == other.index and self.inElevator == other.inElevator

class SimulationStepInfo():
    def __init__(self, building):
        self.passengers = {}
        self.elevatorHeights = {}

        for f in building.floors:
            for p in f.passengerList:
                self.passengers[p.id] = PassengerInfo(False, f.number)

        for e in building.elevators:
            for p in e.passengerList:
                self.passengers[p.id] = PassengerInfo(True, e.elevatorIndex)
            self.elevatorHeights[e.elevatorIndex] = e.currentHeight
    

class GameDisplay():
    def __init__(self, simulation, scale):
        simulation.onStepEnd.add_listener(self.step)
        simulation.onSimulationStarted.add_listener(self.startSimulation)
        self.scale = scale

    def startSimulation(self, simulation):
        building = simulation.building
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
            ele = SpriteEntity(self.frontElevator, self.backElevator, (0,0), (self.totScale,self.totScale))
            self.elevators[e.elevatorIndex] = ele
            self.allSprites.add(ele.back)
            self.allSprites.add(ele.front)

        #Ground
        for y in range(self.buildingMargin[1]):
            for x in range(self.screenTileAmount[0]):
                loc = (x * self.totScale, (self.screenTileAmount[1] - y - 1) * self.totScale)
                self.allSprites.add(Sprite(self.whiteTile, loc, (self.totScale, self.totScale), self.greyColor))

        self.passengers = {}
        self.stepInfo = None



    def getShaftLocation(self, elevatorIndex):
        return self.additionalBuildingWidth + elevatorIndex
    
    def getPassengerYCoord(self, passengerInfo):
        if(passengerInfo.inElevator):
            return self.elevators[passengerInfo.index].screenLoc[1]
        else:
            return ((self.floorAmount - 1 - self.floorAmount) + self.buildingMargin[1]) * self.totScale

            
    def getRandomPassengerLocation(self, passengerInfo):
        if(passengerInfo.inElevator):
            return ((random.randrange(0, 1) + self.getShaftLocation(passengerInfo.index) + self.buildingMargin[0]) * self.totScale, 
                    self.getPassengerYCoord(passengerInfo))
        else:
            return mul((random.randrange(0, self.buildingWidth) + self.buildingMargin[0], 
                          (self.floorAmount - 1 - self.floorAmount) + self.buildingMargin[1]), 
                          self.totScale)

    def applyDifferences(self, stepInfo, lastStepInfo):
        for key in stepInfo.elevatorHeights:
            val = stepInfo.elevatorHeights[key]
            elevator = self.elevators[key]
            elevator.updateScreenLoc(mul(
                (self.getShaftLocation(key) + self.buildingMargin[0], 
                (self.floorAmount - 1 - val/100) + self.buildingMargin[1]), 
                self.totScale))
            
            #Did not move this turn, open door
            if(val == lastStepInfo.elevatorHeights[key]):
                elevator.back.rect.topleft = (-50,-50)

        for key in stepInfo.passengers:
            val = stepInfo.passengers[key]
            if(key not in self.passengers):     #Spawn new passenger
                loc = self.getRandomPassengerLocation(val)
                pas = SpriteEntity(self.passengerClothes, self.passengerSkin, loc, mul((10,19), self.scale), self.floorColors[val.index])
                self.passengers[key] = pas
                self.allSprites.add(pas.back)
                self.allSprites.add(pas.front)

            elif not val.equal(lastStepInfo.passengers[key]):  #Switched floor
                loc = self.getRandomPassengerLocation(val)
                self.passengers[key].updateScreenLoc(loc)

            else:                                              #Height update
                p = self.passengers[key]
                loc = (p.screenLoc[0], self.getPassengerYCoord(val))
                p.updateScreenLoc(loc)

        for key in lastStepInfo.passengers:
            if key not in stepInfo.passengers:          #Passenger removed
                val = self.passengers[key]
                self.allSprites.remove(val.front)
                self.allSprites.remove(val.back)

            



    def step(self, simulation):
        building = simulation.building
        lastStepInfo = self.stepInfo
        self.stepInfo = SimulationStepInfo(building)
        if(lastStepInfo != None):
            self.applyDifferences(self.stepInfo, lastStepInfo)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.screen.fill(self.backgroundColor)
        self.allSprites.update()
        self.allSprites.draw(self.screen)


        # Update the display
        pygame.display.flip()

