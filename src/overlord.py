from multiprocessing import Pool
import queue
import numpy as np
import main
from map import Map
from mapsimulation import SimulationData
from pathprimitiveplanner import PrimitivePathPlanner
from entitymanager import EntityManager
import pygame
from pygame.locals import *
import random
from entitytarget import EntityTarget
from agent import Agent
from pathgeneratorsmooth import PathGeneratorSmooth
from pathgeneratorstraight import PathGeneratorStraight
import os, sys
import displayPaths


def run_simulations(next):
    (a,i,j,k,l,o) = next
    print('Starting simulation ({},{},{},{},{})'.format(i,j,k,l,o))
    s = main.RunSimulation(a)
    print('Saving output of simulation ({},{},{},{},{})'.format(i,j,k,l,o))
    #f = open(str(o)+"/"+str(i)+"/"+str(j)+"/"+str(k)+"/"+str(l)+".txt",'w')
    f = open("test.txt", 'w+')
    f.write(s)
    f.close()
    print('Finished simulation ({},{},{},{},{})'.format(i,j,k,l,o))


def run_threads(start_map, stop_map, num_threads):
    #for i in range(start_map, stop_map): #33 maps
    taskList = []
        #print('Adding map {} to the queue...'.format(i), end='')
        #if i < 13:
        #    m = Map(100, 100, 1, 1, 50, np.loadtxt("saved data maps/notrand" + str(i + 1)+".txt")[:100])
        #else:
        #    m = Map(100, 100, 1, 1, 50, np.loadtxt("saved data maps/rand" + str(i - 12)+".txt")[:100])
        #import maps
    #m1 = Map(100, 100, 1, 1, 50, np.loadtxt("saved data maps/Rand8.txt")[:100])
    #m2 = Map(100, 100, 1, 1, 50, np.loadtxt("saved data maps/Rand9.txt")[:100])
    entropy = np.loadtxt("../data/new_entropy_upsampled.txt")[:200]
    m1 = Map(200, 200, 1, 1, 50, entropy)
    m2 = Map(200, 200, 1, 1, 50, np.loadtxt("../data/new_shade_map.txt")[:200])
    m3 = Map(200, 200, 1, 1, 50, np.loadtxt("../data/new_risk_map.txt")[:200])
    path_time, no_samples, replan_ratio = 50, 15, 0.5
    generator = PathGeneratorStraight(path_time)
    #generator = PathGeneratorSmooth(0.95, (1, 5), (8, 16), path_time)
    testPlanner = PrimitivePathPlanner(replan_ratio * path_time, no_samples, [generator],[m1,m2,m3],3)  # replanTime, tries, generators, initialMaps
    testEntityManager = EntityManager()
    agent = testEntityManager.spawnEntity(Agent, (100, 100), 0)
    testPlanner.registerNewAgent(agent)
    agent.generatorIndex = 0
    agent.mapSplitIndex = 0
    '''for j in range(1): #10 sets of targets
            dk = []
            for ll in range (1):
                dk.append(m.getRandomPoint())
            for k in range(1): # 3 sets of agent setup
                for l in range(1): # 20 trials per setup
                    for o in range(1): # split map or not
                        path_time, no_samples, replan_ratio = 50, 15, 0.5
                        generator = PathGeneratorSmooth(0.2, (1, 5), (8, 12), path_time) # straightChance, pathLengthRange, radiusRange, pathTime
                        #generator = PathGeneratorSmooth(0.2, (1, 10), (15, 25), path_time) # WIDE # straightChance, pathLengthRange, radiusRange, pathTime
                        generator2 = PathGeneratorStraight(path_time)
                        testPlanner = PrimitivePathPlanner(replan_ratio * path_time, no_samples, [generator,generator2], m) # replanTime, tries, generators, initialMap
                        testEntityManager = EntityManager()

                        for ii in range(1):  # setting each agent
                            agent = testEntityManager.spawnEntity(Agent, (50, 50), 0)
                            testPlanner.registerNewAgent(agent)
                            if ii < 5 : # <7 for primitive-spot_omni-details, <3
                                agent.mapSplitIndex = 2 #1, 2
                            else :
                                agent.mapSplitIndex = 1 #2, 1
                            if k == 0 :
                                if ii < 2 :
                                    agent.generatorIndex = 0
                                else :
                                    agent.generatorIndex = 1
                            elif k == 1 :
                                if ii < 5 :
                                    agent.generatorIndex = 0
                                else :
                                    agent.generatorIndex = 1
                            elif k == 2 :
                                if ii < 8 :
                                    agent.generatorIndex = 0
                                else :
                                    agent.generatorIndex = 1
                            if o == 0 :
                                agent.mapSplitIndex = 0

                        for jj in range(1): # putting targets into entitymanager
                            e = testEntityManager.spawnEntity(EntityTarget, dk[jj], 0)
                            '''
    taskList.append((SimulationData([m1,m2,m3], testPlanner, testEntityManager),0,0,0,0,0))
    random.shuffle(taskList)
    print('OK')

    p = Pool(num_threads)
    p.map(run_simulations, taskList)
    print("gets here")
    displayPaths.runDisplay(taskList, 0)

        #displayPaths.runDisplay(taskList, 0)  # taskList, displayType (0 - probability map, 1 - terrain, 2 - both, 3 - info map, 4 - info and probability maps, 5 - coarse reconstructed and probability maps, 6 - gaussians)


if __name__ == "__main__":
    num_threads = 1
    start_map, stop_map = 10, 11

    if len(sys.argv) == 2:
        start_map    = int(sys.argv[1])
        stop_map     = start_map + 1
    elif len(sys.argv) == 3:
        start_map    = int(sys.argv[1])
        stop_map     = int(sys.argv[2])
    elif len(sys.argv) == 4:
        start_map    = int(sys.argv[1])
        stop_map     = int(sys.argv[2])
        num_threads  = int(sys.argv[3])

    print('Starting tests from map {:d} until map {:d} with {:d} threads...'.format(start_map, stop_map, num_threads))
    run_threads(start_map, stop_map, num_threads)
