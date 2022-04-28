from pathgenerator import PathGenerator
from pathprimitive import PathPrimitive
from primitiveline import PrimitiveLine
from primitivecurve import PrimitiveCurve
import random as rand
import numpy as np

class PathGeneratorSmooth(PathGenerator):

    def __init__(self, straightChance, pathLengthRange, radiusRange, pathTime):
        self._straightChance = straightChance
        self._pathLengthRange = pathLengthRange
        self._radiusRange = radiusRange
        self._pathTime = pathTime
        self._primitiveTries = 5

    #TODO: Obstacle avoidance + speeds
    def generateRandomPrimitivePath(self, map, agent):
        ''' Returns an array of primitives corresponding to a path for the given agent

            Args:
                map         (Map): Map to generate path on
                agent       (Agent): Agent to generate path for
        '''
        inBounds = True
        primitivePath = []
        timeLeft = self._pathTime
        heading = agent.rotation
        speed = agent.currentSpeed
        point = map.mapToWorld(agent.position[0], agent.position[1])
        firstPrimitive = True
        while timeLeft > 0:
            primitiveAttempts = self._primitiveTries
            inBounds = False
            primitive = None
            time = 0

            while inBounds == False and primitiveAttempts > 0:
                (pathTimeMin, pathTimeMax) = self._pathLengthRange
                time = min(rand.uniform(pathTimeMin, pathTimeMax), timeLeft)
                if (rand.random() < self._straightChance):
                    primitive = PrimitiveLine(time, speed, point, heading)
                else:
                    (radiusMin, radiusMax) = self._radiusRange
                    radius = rand.uniform(max(radiusMin, agent.minRadius), radiusMax)
                    dir = 1 + ((rand.random() < 0.5) * -2)
                    primitive = PrimitiveCurve(time, speed, point, heading, radius, dir)
                inBounds = primitive.isInMapBounds(map) or (firstPrimitive and not map.isWorldPointOutOfBounds( primitive.getEndPoint() ))
                primitiveAttempts -= 1
            if inBounds == False:
                break
            else:
                timeLeft -= time
                heading = primitive.getEndHeading()
                point = primitive.getEndPoint()
                minSpeed = max(speed - agent.acceleration * time, agent.minSpeed)
                maxSpeed = min(speed + agent.acceleration * time, agent.maxSpeed)
                speed = rand.uniform(minSpeed, maxSpeed)
                primitivePath = np.append(primitivePath, [primitive])
                firstPrimitive = False

        return (PathPrimitive(primitivePath),inBounds)