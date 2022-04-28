from map import Map
from entity import Entity
from entitytarget import EntityTarget
import mathlib
import pygame
import numpy as np

class Agent(Entity):
    '''Stores information of an agent.
        Attributes:
            startPt           (int, int): starting point of the agent
            
    '''

    def onSpawned(self):
        self.startPt = self.position
        self.minRadius = 2
        self.heading = 0
        (self.normalSpeed, self.minSpeed, self.maxSpeed, self.acceleration) = (4, 1, 6, 0)
        self.currentSpeed = self.normalSpeed
        self.path = None
        self.visionRadius = 5
        self.visionfwhm = 4
        self.visionMap = mathlib.makeGaussian(2*self.visionRadius,2*self.visionRadius,self.visionfwhm)
        self.probeTime = 0.1
        self.probeTimeCurrent = 0
        self.pathTime = 0
        self.size = 10.0
        self.drawHeading = True
        self.image = None
        self.generatorIndex = 0
        self.findChance = 0.3
        self.splitMapIndex = 0 #0 - No split map, 1 - Primitive split map, 2- omnidirectional split map

    def onActivated(self):
        pass#self.image = pygame.image.load("UAV.png").convert_alpha()

    def setNewPath(self, newPath):
        self.path = newPath
        self.pathTime = 0

    def tick(self, deltaTime, world):
        if (len(self.path.primitiveList) > 0 and self.path.getTotalTime() > self.pathTime):
            self.pathTime += deltaTime
            self.position = self.path.getPointAtTime(self.pathTime)
            self.rotation = self.path.getHeadingAtTime(self.pathTime)
            self.probeTimeCurrent += deltaTime
            if( self.probeTimeCurrent > self.probeTime):
                self.probeTimeCurrent = 0
                self.attemptObservation(world)

    def attemptObservation(self, world):
        reportFlag = False
        time = world.getTimePassed()
        for ent in world.getAllEntities():
            r = self.visionRadius
            if isinstance(ent, EntityTarget) and self.distanceTo(ent) <= self.visionRadius:
                x = ent.position[0]
                y = ent.position[1]
                (entx_m, enty_m) = world.map.worldToMap(x, y)
                (posx_m, posy_m) = world.map.worldToMap(self.position[0], self.position[1])
                (ent_posx_g, ent_posy_g) = (entx_m + r - posx_m, enty_m + r - posy_m)
                if(min(ent_posx_g, ent_posy_g) >= 0 and max(ent_posx_g, ent_posy_g) < 2*r):
                    prob_detected = self.findChance * self.visionMap[ent_posx_g][ent_posy_g] / self.visionMap[r][r]
                    if np.random.uniform() < prob_detected and ent.spotted == False:
                        world.pathPlanner.reportObservation(self, ([time, x, y], 1))
                        ent.spot()
                        reportFlag = True
        if reportFlag == False:
            x = self.position[0]
            y = self.position[1]
            world.pathPlanner.reportObservation(self, ([time, x, y], 0))

    def getInfoUnderMap(self, map):
        infoVal = 0
        visionMap = self.visionMap / np.max(self.visionMap)
        for vX in range(0, len(visionMap)):
            for vY in range(0, len(visionMap[0])):
                (x,y) = map.worldToMap(self.position[0], self.position[1])
                mapX = x + vX - len(visionMap) // 2
                mapY = y + vY - len(visionMap[0]) // 2
                if mapX >= 0 and mapX < len(map.getDistribution()) and mapY >= 0 and mapY < len(map.getDistribution()[0]):
                    infoVal += (visionMap[vX][vY] * map.getDistribution()[mapX][mapY])
        #print("Info is: " + str(infoVal))
        return infoVal
#111
