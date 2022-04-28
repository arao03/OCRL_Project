import math
import random
from entity import Entity

class EntityTarget(Entity):
    '''Base class for all real-time simulatable objects.

    '''

    def onSpawned(self):
        self.moveSpeed = 5
        self.spotted = False


    def tick(self, deltaTime, world):
        moveAngle = random.random() * 2 * math.pi
        moveDist = deltaTime * self.moveSpeed
        moveVector = (moveDist * math.cos(moveAngle), -moveDist * math.sin(moveAngle))
        self.addPosition(moveVector)

    def spot(self):
        self.spotted = True
        self.color = (255,0,0)