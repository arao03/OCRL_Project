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
    #m1 = Map(100, 100, 1, 1, 50, np.loadtxt("saved data maps/notrand1.txt")[:100])
    #m2 = Map(100, 100, 1, 1, 50, np.loadtxt("saved data maps/Rand9.txt")[:100])
    entropy = np.loadtxt("../data/new_entropy_upsampled.txt")[:200]
    m1 = Map(200, 200, 1, 1, 50, entropy)
    m2 = Map(200, 200, 1, 1, 50, np.loadtxt("../data/new_shade_map.txt")[:200])
    m3 = Map(200, 200, 1, 1, 50, np.loadtxt("../data/new_risk_map.txt")[:200])
    print(m3._distribution)
    path_time, no_samples, replan_ratio = 100, 25, 0.5
    #generator = PathGeneratorStraight(path_time)
    generator = PathGeneratorSmooth(0.9, (1, 3), (8, 10), path_time)
    testPlanner = PrimitivePathPlanner(replan_ratio * path_time, no_samples, [generator],[m1,m2,m3],3)  # replanTime, tries, generators, initialMaps
    testEntityManager = EntityManager()
    agent = testEntityManager.spawnEntity(Agent, (100, 100), 0)
    testPlanner.registerNewAgent(agent)
    agent.generatorIndex = 0
    agent.mapSplitIndex = 0

    run_simulations((SimulationData([m1,m2,m3], testPlanner, testEntityManager),0,0,0,0,0))
    #random.shuffle(taskList)
    #print('OK')

    #p = Pool(num_threads)
    #p.map(run_simulations, taskList)
    #print("gets here")
    #displayPaths.runDisplay(taskList, 0)

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
