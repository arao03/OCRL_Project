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
import copy
from HypothesisMap.hypo_map.hsi import HSI
from HypothesisMap.hypo_map.model import HypothesisMap
from HypothesisMap.hypo_map.classifier import Classifier
from HypothesisMap.classes.classifiers import DCDM
import matplotlib.pyplot as plt

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

        ############ Instantiate Hypothesis Map ############
        coder = 'vae'
        n_dim = 6
        threshold = 0.0
        classes_ = np.array([0,3,4])
        datadir = 'HypothesisMap/datadir/Cuprite/'
        i_lim, j_lim = [1070,1270], [1550,1750]

        ######## Hyperspectral Cube ########

        hsi_params = dict(
            filename = datadir + 'aster/' +'aviris_aster_cube_norm.npy',
            wavelengths = np.load(datadir + 'aster/' + 'aster_wavelengths.npy'),
            rgb_filename = datadir + 'aviris/' + 'aviris_rgb.npy',
            valid_filename = None,
            dem_filename = datadir + 'terrain/' + 'cuprite_dem_aster.npy',
            slope_filename = datadir + 'terrain/' + 'cuprite_slope_both_central.npy',
            classes_filename = None,
            H = np.load(datadir + 'coordinates/' + 'H_gps2pix.npy'), # maps from pixels to lat, lon
            resolution = 3.7, spatial_factor = 4, spectral_factor = 1,
            i_lim = i_lim, j_lim = j_lim, k_lim = None,
            norm = 'min-max',
            valid_func = None,
            interpolate = True)

        self.aster = HSI(**hsi_params)

        aviris_params = copy.deepcopy(hsi_params)
        aviris_params['filename'] = datadir  + 'aviris/' + 'aviris_cube_2um_norm.npy'
        aviris_params['wavelengths'] = np.load(datadir + 'aviris/' + 'aviris_wavelengths_2um.npy')
        aviris_params['norm'] = 'min-max'
        aviris_params['classes_filename'] = None
        aviris_params['k_lim'] = [1,79]

        self.aviris = HSI(**aviris_params)

        prism_params = copy.deepcopy(aviris_params)
        prism_params['spatial_factor'] = 1

        self.prism = HSI(**prism_params)

        ######## Gaussian Process ########

        gp_params = dict(
            dimx = self.aster.bands, dimy = n_dim, mult = True, prior = False, spatial = True, spatial_dim = 2, 
            stationary = True, kernel = 'RBF', n_opt = True, p_opt = True, l_opt = True,
            noise_std = 0.082541, p = 1.0, length_scale = np.array([2.02243809e+04, 4.57488270e-01]),
            stationary_weight = 1.0, length_split = [2,self.aster.bands],
            bounds = (1e-3,1e5), optimizer = 'L-BFGS-B', n_restarts_optimizer=100)
        dcgm_params = None

        ######## Coder ########

        if coder == 'pca':
            ### PCA ###
            coder_params = dict(
                model = 'pca',
                dim_in = 80,
                dim_high = 80,
                dim_low = 6,
                model_file = datadir + 'coders/' + 'aviris_2um_80_PCA_norm.pkl',
                wv_high = np.load(datadir + 'aviris/' + 'aviris_wavelengths_2um.npy'),
                wv_low = np.load(datadir + 'aviris/' + 'aviris_wavelengths_2um.npy'),
                norm = None,
                scale = False)
        else:
            ### VAE ###
            coder_params = dict(
                model = 'ae',
                dim_in = 78,
                dim_high = 78,
                dim_low = 6,
                encoder_file = datadir + 'coders/' + 'ae_6_norm_encoder.best.h5',
                decoder_file = datadir + 'coders/' + 'ae_6_norm_decoder.best.h5',
                wv_high = np.load(datadir + 'coders/' + 'coder_wavelengths.npy'),
                wv_low = np.load(datadir + 'coders/' + 'coder_wavelengths.npy'),
                norm = None)

        ######## Classifier ########

        class_params = dict(
            n_classes = 6,
            model = datadir + 'classifiers/' + 'lr.pkl',
            classes = ['Alunite', 'Buddingtonite', 'Calcite', 'Opal', 'Kaolinite', 'Micas'],
            n_samples = 100)

        cl = Classifier(**class_params)
        self.aviris.classes = self.aviris.vector2cube(cl.predict_proba(self.aviris.cube2vector(self.aviris.cube)))
        self.prism.classes = self.prism.vector2cube(cl.predict_proba(self.prism.cube2vector(self.prism.cube)))

        ######## Hypothesis Map ########
        self.hypothesis_map = HypothesisMap(hsi_params,gp_params,coder_params=coder_params,dcgm_params=dcgm_params,class_params=class_params)

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

        # for m in range(self.nMaps):
        # map = maps[m]
        # nx = (map.sizeX - 1) * map.dX
        # ny = (map.sizeY - 1) * map.dY
        # x = np.linspace(0, nx, map.sizeX)
        # y = np.linspace(0, ny, map.sizeY)
        # X, Y = np.meshgrid(x, y)
        # ell = np.array([5, 5, 5])

        #for m in range(self.nMaps):

        #if( len(dataArray) > 0):
        #    updateMap = gpupdate.GPUpdate(self.initialMaps[m]._distribution, X,Y,np.matrix(dataArray),np.array(stateArray), time, ell, 1)
        #    updateMap = np.transpose(updateMap)
        #    map.updateMapDistribution( updateMap / updateMap.sum())

        self.splitMapPaths = self.generatePrimitivePaths(maps, self._splitMapAgents, self._tries)

        for splitMapIndex in range(len(self._splitMapAgents)):
            agentList = self._splitMapAgents[splitMapIndex]
            for i in range(len(agentList)):
                agentList[i].setNewPath(self.splitMapPaths[splitMapIndex][i])

        print("UPDATING HYPOTHESIS MAP")
        # Update hypothesis map and entropy map
        (i0, j0) = self.splitMapPaths[0][0].getPointAtTime(-1)
        lat, lon = self.aviris.ij2gps(np.floor(i0/4), np.floor(j0/4))
        spectra = self.aviris.gps2spectra(lat,lon)
        self.hypothesis_map.update(spectra,lat,lon)

        # Put the new entropy map into the correct format
        entropy = list(self.hypothesis_map.entropy())[1]
        for i in range(0, len(entropy)):
            for j in range(0, len(entropy[0])):
                if np.isnan(entropy[i][j]):
                    entropy[i][j] = 0
        entropy_upsampled = entropy.repeat(4, axis=0).repeat(4, axis=1)
        self.initialMaps[0] = Map(200, 200, 1, 1, 50, entropy_upsampled)
        plt.scatter(i0, j0, c='red', marker='.')
        plt.imshow(entropy_upsampled)
        plt.pause(1)

        # self.infoMaps[m] = Map(map.sizeX, map.sizeY)
        # self.infoMaps[m].updateMapDistribution( self.generateCurrentInfoMap(map, 1.5) )


    def tick(self, deltaTime, world):
        prePlanTime = pygame.time.get_ticks()
        self._replanTimeCurrent += deltaTime
        if( self._replanTimeCurrent >= self._replanTime):
            print("REPLANNING")
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


        allPaths = []
        agentList = splitMapAgents[0]
        allCosts = []
        splitMapIndex = 0
        for trial in range(tries * len(agentList)):
            paths = []
            costs = []
            for i in range(len(agentList)):
                currentAgent = agentList[i]
                generator = self._generators[currentAgent.generatorIndex]
                inBounds = False
                path = PathPrimitive([])
                while inBounds == False:
                    (path, inBounds) = generator.generateRandomPrimitivePath(maps[0], currentAgent)
                paths.append(path)
            for m in range(self.nMaps):
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

        paretoNum = len(np.where(pareto)[0])
        if paretoNum == 0:
            paretoNum = 1
        idx = random.randrange(paretoNum)

        chosenPath = allPaths[idx]
        return np.array([chosenPath])




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
