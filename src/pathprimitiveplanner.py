import operator
import math
from map import Map
import numpy as np
import random as rand
import mathlib
from agent import Agent
from primitiveline import PrimitiveLine
from primitivecurve import PrimitiveCurve
from pathprimitive import PathPrimitive
import pygame
import enum
import gpupdate
import random

class PrimitivePathPlanner():

    def __init__(self, replanTime, tries, generators, initialMaps, nMaps):
        self._replanTime = replanTime
        self._replanTimeCurrent = 0
        self.splitMapPaths = [[],[],[]]
        self._tries = tries
        self._splitMapAgents = [[],[],[]]
        self._generators = generators
        self.observations = []
        self.recordedObservations = []
        self.observationDuration = 20
        self.infoMaps = [[],[], []]
        self.initialMaps = initialMaps
        self.nMaps = nMaps

    def pareto_choices(self, costs):
        """
        Find the pareto-efficient points
        :param costs: An (n_points, n_costs) array
        :return: A (n_points, ) boolean array, indicating whether each point is Pareto efficient
        """
        is_efficient = np.ones(costs.shape[0], dtype=bool)
        for i, c in enumerate(costs):
            is_efficient[i] = np.all(np.any(costs[:i] > c, axis=1)) and np.all(np.any(costs[i + 1:] > c, axis=1))
        return is_efficient

    def getAllAgents(self):
        agents = []
        for agentList in self._splitMapAgents:
            for agent in agentList:
                agents.append(agent)
        return agents

    def reportObservation(self, agent, observation):
        ''' records a new observation in the path planner
        :param agent:
        :param observation:
        :return:
        '''
        (data, type) = observation
        if( type == 1):
            #print("New observation from agent " + str(agent.id) + ": " + str(observation))
            self.recordedObservations.append(observation)
        self.observations.append((data,0))

    def registerNewAgent(self, agent):
        ''' Registers a new agent to plan paths for
        :param agent: (Agent) the new agent to register
        '''
        self._splitMapAgents[agent.splitMapIndex].append(agent)

    def replanPaths(self, maps, time):
        ''' Replans paths for all registered agents for map, considering all current observations
        :param map: (Map) map to plan on
        '''
        #time = pygame.time.get_ticks() / 1000
        clipTime = time - self.observationDuration
        self.observations = [observation for observation in self.observations if observation[0][0] >= clipTime]
        dataArray = []
        stateArray = []
        for observation in self.observations:
            (data, state) = observation
            dataArray.append(data)
            stateArray.append(state)

        for m in range(self.nMaps):
            map = maps[m]
            nx = (map.sizeX - 1) * map.dX
            ny = (map.sizeY - 1) * map.dY
            x = np.linspace(0, nx, map.sizeX)
            y = np.linspace(0, ny, map.sizeY)
            X, Y = np.meshgrid(x, y)
            ell = np.array([5, 5, 5])

            #for m in range(self.nMaps):

            if( len(dataArray) > 0):
                updateMap = gpupdate.GPUpdate(self.initialMaps[m]._distribution, X,Y,np.matrix(dataArray),np.array(stateArray), time, ell, 1)
                updateMap = np.transpose(updateMap)
                map.updateMapDistribution( updateMap / updateMap.sum())

            self.splitMapPaths = self.generatePrimitivePaths(maps, self._splitMapAgents, self._tries)

            for splitMapIndex in range(len(self._splitMapAgents)):
                agentList = self._splitMapAgents[splitMapIndex]
                for i in range(len(agentList)):
                    agentList[i].setNewPath(self.splitMapPaths[splitMapIndex][i])

            self.infoMaps[m] = Map(map.sizeX, map.sizeY)
            self.infoMaps[m].updateMapDistribution( self.generateCurrentInfoMap(map, 1.5) )


    def tick(self, deltaTime, world):
        prePlanTime = pygame.time.get_ticks()
        self._replanTimeCurrent += deltaTime
        if( self._replanTimeCurrent >= self._replanTime):
            self.replanPaths(world.maps, world.getTimePassed())
            self._replanTimeCurrent = 0
        postPlanTime = pygame.time.get_ticks()
        return (postPlanTime - prePlanTime)/1000

    def getAllPaths(self):
        paths = []
        for splitMapIndex in range(len(self.splitMapPaths)):
            for pathIndex in range(len(self.splitMapPaths[splitMapIndex])):
                paths.append(self.splitMapPaths[splitMapIndex][pathIndex])
        return paths

    def generatePrimitivePaths(self, maps, splitMapAgents, tries):
        ''' Returns an array of primitive paths (an array of primitives) that take pathTime time for each agent.
            path at index i corresponds to agent i in agents array.

            Args:
                map         (Map): Map to generate path on
                pathTime    (float): time path traversal should take
                agents      (Agent array): the agents to generate path for
                tries       (int): how many tries should we do for the path
                                   (we pick best one using ergodicity calculation)
        '''


        bestSplitMapPaths = [[],[],[]]
        allPaths = []
        #for splitMapIndex in range(len(splitMapAgents)):
        minErg = -1
        splitMapIndex = 0
        agentList = splitMapAgents[0]
        allCosts = []
        for trial in range(tries * len(agentList)):
            paths = []
            costs = []
            for m in range(self.nMaps):
                for i in range(len(agentList)):
                    currentAgent = agentList[i]
                    generator = self._generators[currentAgent.generatorIndex]
                    inBounds = False
                    path = PathPrimitive([])
                    while inBounds == False:
                        (path, inBounds) = generator.generateRandomPrimitivePath(maps[m], currentAgent)
                    paths.append(path)

                infoMap = self.generateInfoMapFromPrimitivePaths(self.initialMaps[m], 5, agentList, paths)
                if m == 2:
                    cost = mathlib.calcBinary(maps[m], paths, infoMap)
                else:
                    cost = mathlib.calcErgodicity(maps[m], infoMap, splitMapIndex, 15)

                costs.append(cost)

            allPaths.append(paths)
            allCosts.append(costs)

        allCosts = np.array(allCosts)
        allPaths = np.array(allPaths)

        pareto = self.pareto_choices(allCosts)

        #print(np.where(pareto)[0])

        paretoNum = len(np.where(pareto)[0])
        if paretoNum == 0:
            paretoNum = 1
        idx = random.randrange(paretoNum)

        #print(allCosts[idx])

        chosenPath = allPaths[idx]

        bestSplitMapPaths[splitMapIndex] = chosenPath

        return np.array(bestSplitMapPaths)




    def generateCurrentInfoMap(self, map, sampleTime):
        '''
        Generates a info map that is created from all of the currently assigned paths
        :param map: (Map): the map to generate info map for
        :param sampleTime:  (float): how often we should sample a point on the path for the info map
        :return: (Map): generated info map
        '''
        infoMap = np.zeros((map.sizeX, map.sizeY))
        for splitMapIndex in range(len(self.splitMapPaths)):
            if(len(self._splitMapAgents[splitMapIndex]) > 0):
                tempMap = self.generateInfoMapFromPrimitivePaths(map, sampleTime
                                                                ,self._splitMapAgents[splitMapIndex]
                                                                ,self.splitMapPaths[splitMapIndex])
                infoMap += tempMap
        return infoMap

    def generateInfoMapFromPrimitivePaths(self, map, sampleTime, agents, paths ):
        ''' Returns an info map corresponding to the given primitive paths.
            agents[i] should correspond to the path in paths[i] to work correctly

            Args:
                map         (Map): the map to generate info map for
                sampleTime  (float): how often should we sample a point on the path for the info map
                agents      (Agent array): agents to get data from
                paths       (BasePrimitive array array): paths to get info map from
        '''
        infoMap = np.zeros((map.sizeX, map.sizeY))
        for i in range(len(agents)):
            agentInfoMap = self.generateInfoMapFromPrimitivePath(map, sampleTime, agents[i], paths[i])
            infoMap += agentInfoMap
        return infoMap/len(agents)

    def generateInfoMapFromPrimitivePath(self, map, sampleTime, agent, path):
        ''' Returns an info map corresponding to the given primitive paths.
            agents[i] should correspond to the path in paths[i] to work correctly

            Args:
                map         (Map): the map to generate info map for
                sampleTime  (float): how often should we sample a point on the path for the info map
                agent      (Agent): agent to get data from
                path       (BasePrimitive array): path to get info map from
        '''
        infoMap = np.zeros((map.sizeX, map.sizeY))
        pTime = 0
        pIndex = 0
        samples = 0;

        while( pIndex < len(path.primitiveList) ):
            primitive = path.primitiveList[pIndex]
            (pX,pY) = primitive.getPointAtTime(pTime)
            (x,y) = map.worldToMap(pX, pY)

            #TODO: Maybe we can make this in matricial form? Not sure if it will be faster though
            for vX in range (0, len(agent.visionMap)):
                for vY in range (0, len(agent.visionMap[0])):
                    mapX = x + vX - len(agent.visionMap)//2
                    mapY = y + vY - len(agent.visionMap[0])//2
                    if  mapX >= 0 and mapX < len(map.getDistribution()) and mapY >= 0 and mapY < len(map.getDistribution()[0]):
                        infoMap[mapX][mapY] += (agent.visionMap[vX][vY])

            samples += 1
            pTime += sampleTime
            while pTime >= primitive.getTotalTime():
                pTime -= primitive.getTotalTime()
                pIndex += 1
                if pIndex >= len(path.primitiveList):
                    break
                else:
                    primitive = path.primitiveList[pIndex]

        return (infoMap / samples)
