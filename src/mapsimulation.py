import pygame
import numpy as np
from pathprimitiveplanner import PrimitivePathPlanner
from pygame.locals import *
from copy import copy
import mathlib
from map import Map
from agent import Agent
import random
from primitiveline import PrimitiveLine
from primitivecurve import PrimitiveCurve
import math
from entitymanager import EntityManager
from entitytarget import EntityTarget


class SimulationData:

    def __init__(self, maps, pathPlanner, entityManager):
        self.maps = maps
        self.pathPlanner = pathPlanner
        self.entityManager = entityManager
        self.tickTime = 0.5
        self.tickTotal = 500

class MapSimulation:
    '''The main file for controlling the simulation. This is where everything is created and drawn every frame.

        There are 3 coordinate spaces in the simulation:
        World space: represents the real world units in floats
        Map space: represents discrete coordinates on the information map
        Screen space: represents pixel coordinates on the screen

            Attributes:
                screenWidth             (int): width of the windowed screen in pixels
                screenHeight            (int): height of the windowed screen in pixels
                map                     (Map): current map being simulated
                screen                  (Screen): the screen object used to display simulation
                running                 (bool): whether the simulation is currently running
                pathPlanner             (PathPlanner): Used to generate paths for agents
                path                    (Path): Currently chosen path
                entityManager           (EntityManager): manages all of the entities in the simulation
    '''

    PATH_COLOR = (20, 20, 20)
    PATH_START_POINT_COLOR = (100, 200, 0)
    PATH_END_POINT_COLOR = (100, 50, 0)
    PATH_POINT_RADIUS = 2
    PATH_PRIMITIVE_POINT_RADIUS = 2

    PAINTER_INCREASE_STRENGTH = 0.00005
    PAINTER_INCREASE_RADIUS = 20
    PAINTER_REDUCE_STRENGTH = 0.00005
    PAINTER_REDUCE_RADIUS = 20


    def __init__(self, simData, graphicalDisplay=True, screenWidth=1024, screenHeight=1024):
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.maps = simData.maps
        self.pathPlanner = simData.pathPlanner
        self.entityManager = simData.entityManager
        self.graphics = graphicalDisplay
        self.ticksLeft = simData.tickTotal
        self.startTicks = simData.tickTotal
        self.tickTime = simData.tickTime
        self.recordedAgentData = []

        if(self.graphics):
            self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight))
            pygame.display.set_caption('Heterogenous Multi Agent System Simulation')
            background_colour = (255, 255, 255)
            self.screen.fill(background_colour)
            pygame.display.flip()

        for entity in self.entityManager.entityList:
            entity.onActivated()

        self.generateNewPath()
        self.drawList = []
        self.mapMode = 0
        self.spaceReleaseBlock = False
        self.running = True
        self.tick()

    def generateNewPath(self):
        self.pathPlanner.replanPaths(self.maps, self.getTimePassed())
        #print(len(self.pathPlanner.getAllPaths()))


    def getAllEntities(self):
        '''Gets all of the entities that are active in the simulation
        :return: Entity list
        '''
        return self.entityManager.entityList

    def graphicsTick(self):
        self.drawList = []
        drawNotify = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        mapChange = self.painterTick()

        if pygame.key.get_pressed()[pygame.K_SPACE] and self.spaceReleaseBlock != True:
            self.generateNewPath()
            drawNotify = True
            self.spaceReleaseBlock = True
        else:
            self.spaceReleaseBlock = False

        if (self.painterTick()):
            drawNotify = True

        if pygame.key.get_pressed()[pygame.K_e]:
            if (self.mapMode == 0):
                drawNotify = True
            self.mapMode = 1
            mapProbScaleFactor = 0.1
        else:
            if (self.mapMode == 1):
                drawNotify = True
            self.mapMode = 0
            mapProbScaleFactor = 0.4

        if drawNotify:
            mapToDraw = self.maps[0] if self.mapMode == 0 else self.pathPlanner.infoMap
            self.drawProbabilityMap(mapToDraw, mapProbScaleFactor)
            for i in range(0, len(self.pathPlanner.getAllPaths())):
                self.drawPrimitivePath(self.pathPlanner.getAllPaths()[i].primitiveList, 0.1, False)
            pygame.display.update()

    def getTimePassed(self):
        return (self.startTicks - self.ticksLeft) * self.tickTime

    def tick(self):
        '''Main tick function for the simulation. Currently draws map state every frame.
        '''

        #paths = []

        drawNotify = True
        spaceReleaseBlock = False
        deltaTime = 0
        while self.running:

            if( self.graphics ):
                self.graphicsTick()

            self.entityManager.tick(self.tickTime, self)

            if(self.graphics):
                self.drawEntities()

            #print("ticks left " + str(self.ticksLeft))

            if(self.graphics):
                pygame.display.update()

            # DO NOT DELETE THIS COMMENT
            # avoiding issue where waiting for planning accelerates behavior
            skipTime = self.pathPlanner.tick(self.tickTime, self)
            # deltaTime = (self.clock.tick(60)/1000) - skipTime

            tickData = []
            for agent in self.pathPlanner.getAllAgents():
                info = agent.getInfoUnderMap(self.maps[0])
                tickData.append((agent.id, agent.position, info))
            self.recordedAgentData.append(tickData)
            #paths.append(self.pathPlanner.getAllPaths())

            self.ticksLeft -= 1
            if(self.ticksLeft <= 0):
                self.running = False
                #print(paths)
                #paths = np.array(paths)
                #infoMap = self.pathPlanner.generateInfoMapFromPrimitivePaths(self.maps[0], 5, self.pathPlanner.getAllAgents(), paths)
                infoMap = self.pathPlanner.generateInfoMapFromPrimitivePaths(self.maps[0], 5, self.pathPlanner.getAllAgents(), self.pathPlanner.getAllPaths())
                #print(self.pathPlanner.getAllPaths())
                f = open("ergodic_vals_multi_entropy.txt", 'a+')
                f.write(str(mathlib.calcErgodicity(self.maps[0],infoMap)) + "\n")
                f.close()
                f = open("ergodic_vals_multi_shade.txt", 'a+')
                f.write(str(mathlib.calcErgodicity(self.maps[1], infoMap)) + "\n")
                f.close()
                f = open("ergodic_vals_multi_risk.txt", 'a+')
                f.write(str(mathlib.calcErgodicity(self.maps[2], infoMap)) + "\n")
                f.close()
            # if pygame.time.get_ticks()>20000 :
            #    self.running = False

        if( self. graphics):
            pygame.display.quit()
            pygame.quit()

    def painterTick(self):
        ''' Controls drawing on the information map
        '''
        drawNotify = False
        (b1, b2, b3) = pygame.mouse.get_pressed()
        if( b1 ):
            changeField = mathlib.makeGaussian(self.PAINTER_INCREASE_RADIUS,self.PAINTER_INCREASE_RADIUS,
                                               self.PAINTER_INCREASE_RADIUS/1.5,None, False) * self.PAINTER_INCREASE_STRENGTH
            (x,y) = self.screenToMap(pygame.mouse.get_pos())
            self.maps[0].addDistribToMap(changeField, (x,y))
            drawNotify = True

        elif ( b3 ):
            changeField = mathlib.makeGaussian(self.PAINTER_REDUCE_RADIUS, self.PAINTER_REDUCE_RADIUS,
                                               self.PAINTER_REDUCE_RADIUS/1.5, None,
                                               False) * -self.PAINTER_REDUCE_STRENGTH
            (x, y) = self.screenToMap(pygame.mouse.get_pos())
            self.maps[0].addDistribToMap(changeField, (x, y))
            drawNotify = True

        return drawNotify

    def drawPrimitivePath(self, path, approx = 0.05, separatePrimitives = False):
        '''Draws a primitive path
        :param path: (Path) the path to draw
        :param approx: (float) how well should the drawing program approximate curves (smaller value is better)
        :param separatePrimitives: (bool) should every primitive be separated by a small dot
        :return:
        '''
        for primitive in path:
            self.drawPrimitive(primitive, approx, separatePrimitives)
        if(len(path) > 0):
            pygame.draw.circle(self.screen, self.PATH_START_POINT_COLOR,
                               self.worldToScreen(path[0].getStartPoint()), self.PATH_POINT_RADIUS)
            pygame.draw.circle(self.screen, self.PATH_END_POINT_COLOR,
                               self.worldToScreen(path[len(path)-1].getEndPoint()), self.PATH_POINT_RADIUS)


    def drawPrimitive(self, primitive, approx = 0.05, separatePrimitives = False):
        ''' Draw a given primitive
        :param primitive: (Primitive) the primitive to draw
        :param approx: (float) how well should the drawing program approximate curves (smaller value is better)
        :param separatePrimitives: (bool) should the primitive have a dot on its end
        '''
        if(isinstance(primitive, PrimitiveLine)):
            startPoint = self.worldToScreen(primitive.getStartPoint())
            endPoint = self.worldToScreen(primitive.getEndPoint())
            pygame.draw.line(self.screen, self.PATH_COLOR, startPoint, endPoint)
        elif(isinstance(primitive, PrimitiveCurve)):
            totalTime = primitive.getTotalTime()
            drawTime = 0
            while( drawTime < totalTime ):
                nextTime = min(totalTime, drawTime + approx)

                startPoint = self.worldToScreen(primitive.getPointAtTime(drawTime))
                endPoint = self.worldToScreen(primitive.getPointAtTime(nextTime))
                pygame.draw.line(self.screen, self.PATH_COLOR, startPoint, endPoint)
                #pygame.draw.circle(self.screen, self.PATH_COLOR,
                #                   self.worldToScreen(primitive.getCircleCenter()), 10)
                drawTime = nextTime
        if separatePrimitives:
            pygame.draw.circle(self.screen, self.PATH_COLOR,
                               self.worldToScreen(primitive.getEndPoint()), self.PATH_PRIMITIVE_POINT_RADIUS)

    def worldToScreen(self, worldPoint):
        '''Convert a point in world units to a point in map units (int,int)
            Args:
                worldPoint  (float, float): point in world units
        '''
        x = int(worldPoint[0] * self.screenWidth / (self.maps[0].sizeX * self.maps[0].dX))
        y = int(worldPoint[1] * self.screenHeight / (self.maps[0].sizeY * self.maps[0].dY))
        return (x, y)

    def mapToScreen(self, mapPoint):
        '''Convert a point on the map to a point on the screen (int,int)
                Args:
                    mapPoint   (int,int): point on the map
        '''
        x = int(mapPoint[0] * self.screenWidth / self.maps[0].sizeX)
        y = int(mapPoint[1] * self.screenHeight / self.maps[0].sizeY)
        return (x, y)

    def screenToMap(self, screenPoint):
        '''Convert a point on the screen to a point on the discrete map (int, int)
            Args:
                screenPoint     (int, int): point on the screen
        '''
        x = int(screenPoint[0] * self.maps[0].sizeX /self.screenWidth)
        y = int(screenPoint[1] * self.maps[0].sizeY /self.screenHeight)
        return (x, y)

    def drawPointPath(self, path, agent):
        '''Draw the given point path
            Args:
                path ((int, int) list): the list of points that represents the path
        '''
        scaledPath = copy(path)
        for i in range(len(path)):
            (x,y) = path[i]
            scaledX = int(x*(self.screenWidth/self.maps[0].sizeX))
            scaledY = int(y*(self.screenHeight/self.maps[0].sizeY))
            scaledPath[i] = (scaledX,scaledY)
            if i == 0:
                pointCol = self.PATH_START_POINT_COLOR
            elif i == (len(path) - 1):
                pointCol = self.PATH_END_POINT_COLOR
            else:
                pointCol = self.PATH_COLOR
            pygame.draw.circle(self.screen, pointCol, scaledPath[i], self.PATH_POINT_RADIUS )
            if i>0:
                speed = agent.speedlist[i-1]
                g=round((speed-agent.minspeed)/(agent.maxspeed-agent.minspeed)*255)
                cPath = [scaledPath[i-1],scaledPath[i]]
                pygame.draw.lines(self.screen, (0,g,0), False, cPath)

    def drawProbabilityMap(self, map, scaleFactor):
        '''Draw the probability map based on the current map (screen still needs to be flipped
           after calling though!)
            Args:
                map             (Map): The map to draw
                scaleFactor     (float): Used to scale the intensity of the colours in the map. The lower the higher
                                         the contrast
        '''
        avg = map.getAvgPointProbability()
        for x in range(map.sizeX):
            for y in range(map.sizeY):
                probMod = (((map.getPointProbability(x,y) / avg) - scaleFactor) *scaleFactor) + scaleFactor
                colVal = np.clip(255*probMod, 0, 255)
                col = (125, colVal, colVal)
                #if (not self.obstacleMap[x][y]):
                #    col = (0, 0, 0)
                rectWidth = (self.screenWidth/map.sizeX)
                rectHeight = (self.screenHeight/map.sizeY)
                fillArea = Rect(x*rectWidth, y*rectWidth, rectWidth, rectHeight)
                self.screen.fill(col, fillArea)

    def drawEntities(self):
        '''Draw all the entities registered in the entity manager
        '''
        for ent in self.entityManager.entityList:
            startPoint = self.worldToScreen(ent.position)
            ex = ent.position[0] + (ent.size/6) * math.cos(ent.rotation)
            ey = ent.position[1] - (ent.size/6) * math.sin(ent.rotation)
            endPoint = self.worldToScreen((ex, ey))
            if( ent.image != None):
                rot_image = pygame.transform.rotate(ent.image, 180*ent.rotation/math.pi)
                rot_rect = rot_image.get_rect(center=startPoint)
                self.screen.blit(rot_image, rot_rect)
            else:
                pygame.draw.circle(self.screen, ent.color, startPoint, int(ent.size))
                if( ent.drawHeading ):
                    pygame.draw.line(self.screen, ent.color, startPoint, endPoint)
