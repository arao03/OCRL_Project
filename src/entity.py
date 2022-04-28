import pygame.draw
import math


class Entity:
    '''Base class for all real-time simulatable objects.
        Attributes:
            position        ((float,float)): current world position
            rotation        (float): current rotation of the entity
            world           (MapSimulation): the simulation that the entity exists in
            id              (int): unique id assigned to this entity
            color           ((int,int,int)): the color of the dot representing the entity, if no image
            size            (float): the size of the dot representing the entity, if no image
            drawHeading     (bool): whether the heading for the entity should be drawn
            image           (Image): image to use to represent the entity
    '''

    def __init__(self, spawnPoint, spawnRot, id):
        self.position = spawnPoint
        self.rotation = spawnRot
        self.id = id
        self.color = (0,0,0)
        self.size = 5.0
        self.drawHeading = False
        self.image = None

    def onSpawned(self):
        ''' called when the entity is spawned into the simulation'''
        pass

    def onActivated(self):
        pass

    def onDestroyed(self):
        ''' called when entity is destroyed in the simulation'''
        pass

    def tick(self, deltaTime, world):
        ''' Called every frame
        :param deltaTime:  time that passed between this frame and last frame.
        '''
        pass

    def addPosition(self, offsetPos):
        '''Adds a vector to the current position
        :param offsetPos: (float,float) 2D vector to add
        '''
        x = self.position[0] + offsetPos[0]
        y = self.position[1] + offsetPos[1]
        self.position = (x,y)

    def distanceTo(self, other):
        '''Gets distance to other entity
        :param other: (Entity) entity to get distance to'''
        xDif = self.position[0] - other.position[0]
        yDif = self.position[1] - other.position[1]
        return math.sqrt(xDif*xDif + yDif*yDif)
