from pathgenerator import PathGenerator
from pathprimitive import PathPrimitive
from primitiveline import PrimitiveLine
from primitivecurve import PrimitiveCurve
import random as rand
import numpy as np
import math

class PathGeneratorStraight(PathGenerator):

    def __init__(self, pathTime):
        self._pathTime = pathTime

    #TODO: Obstacle avoidance + speeds
    def generateRandomPrimitivePath(self, map, agent):
        ''' Returns an array of primitives corresponding to a path for the given agent

            Args:
                map         (Map): Map to generate path on
                pathTIme    (float): How long should travelling on the path take?
                agent       (Agent): Agent to generate path for
        '''
        primitivePath = []
        speed = agent.currentSpeed
        timeLeft = self._pathTime
        point = map.mapToWorld(agent.position[0], agent.position[1])

        while timeLeft > 0:
            print(timeLeft)
            #dist = 1000
            #heading = -1000
            """count = 0
            while True:
                nextPoint = map.getRandomPoint()
                dist = ((point[0] - nextPoint[0]) ** 2 + (point[1] - nextPoint[1]) ** 2) ** 0.5
                heading = math.atan2(-(nextPoint[1]-point[1]), nextPoint[0] - point[0]) #- agent.heading
                if heading < 0:
                    heading = 2*math.pi + heading
                heading = heading - agent.heading
                #print(heading < 2*math.pi)
                if (heading <3*math.pi/2): #and (dist < 80)):
                    break
                else:
                    count+=1
                if count > 10:
                    nextPoint = point
                    dist = ((point[0] - nextPoint[0]) ** 2 + (point[1] - nextPoint[1]) ** 2) ** 0.5
                    heading = math.atan2(-(nextPoint[1]-point[1]), nextPoint[0] - point[0])
                    break

                #print(heading)
                #if heading < 0:
                    #print(heading)

            """
            dist = 20
            count = 0 
            while True:
                heading = np.random.uniform() * 4*math.pi/5 - agent.rotation
                #print(count)
                #print(dist)
                time = min( dist/speed, timeLeft)
                primitive = PrimitiveLine(time, speed, point, heading)
                newPoint = primitive.getEndPoint()
                if newPoint[0] > 0 and newPoint[0] < 200 and newPoint[1] > 0 and newPoint[1] < 200:
                    point = newPoint
                    break
                elif count > 100:
                    nextPoint = map.getRandomPoint()
                    dist = ((point[0] - nextPoint[0]) ** 2 + (point[1] - nextPoint[1]) ** 2) ** 0.5
                    heading = math.atan2(-(nextPoint[1]-point[1]), nextPoint[0] - point[0]) - agent.heading
                    break
                else:
                    count+=1
                    #print("oh no!")

            #print(count)
            
            timeLeft -= time
            minSpeed = max(speed - agent.acceleration * time, agent.minSpeed)
            maxSpeed = min(speed + agent.acceleration * time, agent.maxSpeed)
            speed = rand.uniform(minSpeed, maxSpeed)
            primitivePath = np.append(primitivePath, [primitive])
        return (PathPrimitive(primitivePath),True)