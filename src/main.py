from map import Map
from mapsimulation import MapSimulation, SimulationData
from pathprimitiveplanner import PrimitivePathPlanner
from entitymanager import EntityManager
import pygame
from pygame.locals import *
import random
from entitytarget import EntityTarget
from agent import Agent
from pathgeneratorsmooth import PathGeneratorSmooth
from pathgeneratorstraight import PathGeneratorStraight
import numpy as np


def StartSimulation():
    testMap = Map(100, 100, 1, 1, 50, np.loadtxt("saved data maps/notrand" + str(5) + ".txt")[:100])
    generator = PathGeneratorSmooth(0.2, (2,5), (8,12), 50)
    generator2 = PathGeneratorStraight(50)
    testPlanner = PrimitivePathPlanner(10, 1, [generator, generator2], testMap)
    testEntityManager = EntityManager()
#    clock = pygame.time.Clock()
    testSimulation = SimulationData(testMap, testPlanner, testEntityManager)
    dk = []
    for ll in range(10):
        dk.append(testMap.getRandomPoint())
    for jj in range(10):  # putting targets into entitymanager
        e = testEntityManager.spawnEntity(EntityTarget, dk[jj], 0)
        e.moveSpeed = 0

    for i in range(4):
        agent = testEntityManager.spawnEntity(Agent, (10, 10), 0)
        agent.splitMapIndex = 1
        testPlanner.registerNewAgent(agent)
    for i in range(4):
        agent = testEntityManager.spawnEntity(Agent, (10, 10), 0)
        agent.generatorIndex = 1
        agent.splitMapIndex = 2
        testPlanner.registerNewAgent(agent)

    print(RunSimulation(testSimulation))
def exportObservations(simulationData, sim):
    allObservations=sim.pathPlanner.recordedObservations #index --> time
    observationInfo=[]
    targetsFound=[]

    for currObservation in allObservations:
        found = currObservation[1]
        time = currObservation[0][0]
        x = currObservation[0][1]#target position x
        y = currObservation[0][2]#target position y
        currInfo = "time:"+str(time)+(", found target at(%f,%f)" %(x,y))
        if found == 1 and (x,y) not in targetsFound:
            observationInfo.append(currInfo)
            targetsFound.append((x,y))
    observationText = "\n".join(observationInfo)


    stepInfo = []
    a = sim.recordedAgentData
    f = open("data.txt", 'a+')
    for i in range(len(a)):
        for j in range(len(a[0])):
            f.write(str(a[i][j][1][0]) + " ")
            f.write(str(a[i][j][1][1]) + " ")
        f.write('-1 ')
    f.close()
    f = open("trajectory.txt", 'a+')
    for i in range(0, len(a)):
        agentInfo = []
        for j in range(0, len(a[i])):
            (id,(x,y),z) = a[i][j]
            f.write(str(x) + " " + str(y) + '\n')
            agentInfo.append("Step: "+ str(i) + " AgentID: "+str(id)+" Position: ("+str(x)+","+str(y)+") ObservedInfo: " +str(z))
        stepInfo.append("\n".join(agentInfo))
    f.close()
    allstepinfo = "\n".join(stepInfo)

    return observationText+"\n"+allstepinfo

def RunSimulation( simulationData ):
    sim = MapSimulation( simulationData, True, 700, 700)
    return exportObservations(simulationData, sim)
