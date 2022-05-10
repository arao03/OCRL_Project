import matplotlib.pyplot as plt
import numpy as np
import time
from matplotlib.patches import Circle
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from mpl_toolkits.mplot3d import Axes3D
from itertools import product
from scipy import fftpack
from PIL import Image

#TODO: implement color code for types of agents
#TODO: get rid of hardcoded list lengths

def displayGaussians(next):
    (a,i,j,k,l,o) = next
    no_agents = len(a.entityManager.entityList)//2
    print(no_agents)
    g = np.loadtxt("saved data/gaussians/g.txt")
    gaussians = [[[]]]
    j = 0
    k = 0
    for element in g:
        if (element == -1) and (j < a.entityManager.entityList[k].visionRadius*2-1):
            gaussians[k].append([])
            j+=1
        elif (element == -2) and (k < no_agents-1):
            gaussians.append([[]])
            k+=1
            j = 0
        else:
            if (element >= 0):
                gaussians[k][j].append(element)
    fig, ax = plt.subplots(1)
    print(gaussians)
    for gaussian in gaussians:
        ax.imshow(gaussian)
        plt.show(block=False)
        plt.pause(1)
    plt.show()


def displayPathsonInfoandProbability(next, live):
    (a,i,j,k,l,o) = next
    im = np.loadtxt("saved data/info maps/infoMapDistributionData.txt")
    infoMaps = [[[]]]
    j = 0
    k = 0
    for element in im:
        if (element == -1) and (j != 99):
            infoMaps[k].append([])
            j+=1
        elif (element == -2) and (k != 10):
            infoMaps.append([[]])
            k+=1
            j = 0
        else:
            if (element >= 0):
                infoMaps[k][j].append(float(element))
    sf = np.loadtxt("saved data/agents/a.txt")
    sensorFootprints = [[],[],[],[],[],[],[],[],[],[]]
    for i in range(len(sf)):
        if (sf[i] != -1):
            sensorFootprints[i].append(sf[i])
    print(sensorFootprints)
    for x in sensorFootprints:
        if len(x) == 0:
            x.append(1.0)
    s = np.loadtxt("saved data/paths/data.txt")
    points = [[]]
    j = 0
    for i in range(len(s)):
        if (s[i] == -1):
            points.append([])
            j+=1
        else:
            points[j].append(s[i])
    print(len(points))
    fig, (ax1, ax2) = plt.subplots(1,2)
    ax1.set_aspect('equal')
    ax2.set_aspect('equal')
    ax2.imshow(a.map._distribution)
    displaypoints = [[[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]]]
    for pl in range(len(points)):
        pointlist = points[pl]
        ma = infoMaps[pl//50]
        map = np.array(ma)
        for i in range(len(map)):
            map[i] = np.array(ma[i])
        ax1.clear()
        ax2.clear()
        ax1.imshow(map.transpose())
        ax2.imshow(a.map._distribution)
        for i in range(0,len(pointlist), 2):
            displaypoints[i//2][0].append(pointlist[i])
            displaypoints[i//2][1].append(pointlist[i+1])
        for i in range(10):
            ax1.plot(displaypoints[i][0], displaypoints[i][1])
            ax2.plot(displaypoints[i][0], displaypoints[i][1])
            if len(displaypoints[i][0]) > 0:
                circ1 = Circle((displaypoints[i][0][-1],displaypoints[i][1][-1]),int(sensorFootprints[i][0]),ec='pink',fc='none')
                circ2 = Circle((displaypoints[i][0][-1],displaypoints[i][1][-1]),int(sensorFootprints[i][0]),ec='pink',fc='none')
                ax1.add_artist(circ1)
                ax2.add_artist(circ2)
        if (live):
            plt.show(block=False)
            plt.pause(0.00000000001)
    plt.show()
    print(len(infoMaps))


def displayInfoMaps(next):
    (a,i,j,k,l,o) = next
    im = np.loadtxt("saved data/info maps/infoMapDistributionData.txt")
    infoMaps = [[[]]]
    j = 0
    k = 0
    for element in im:
        if (element == -1) and (j != 99):
            infoMaps[k].append([])
            j+=1
        elif (element == -2) and (k != 10):
            infoMaps.append([[]])
            k+=1
            j = 0
        else:
            if (element >= 0):
                infoMaps[k][j].append(float(element))
    fig,ax = plt.subplots(1)
    ax.set_aspect('equal')
    print(len(infoMaps[0]))
    plt.pause(1)
    for ma in infoMaps:
        map = np.array(ma)
        for i in range(len(map)):
            map[i] = np.array(ma[i])
        ax.imshow(map)
        plt.show(block=False)
        plt.pause(1)
    plt.show()
    print(len(infoMaps))

def displayPathsonProbability(next, live):
    (a,i,j,k,l,o) = next
    fig, (ax1, ax2, ax3) = plt.subplots(1,3)
    ax1.set_aspect('equal')
    ax1.imshow(a.pathPlanner.entropyMaps[0]._distribution, interpolation='nearest')
    ax2.set_aspect('equal')
    ax2.imshow(a.maps[1]._distribution, interpolation='nearest')
    ax3.set_aspect('equal')
    ax3.imshow(a.maps[2]._distribution, interpolation='nearest')
    ax1.title.set_text('Entropy')
    ax2.title.set_text('Shade')
    ax3.title.set_text('Risk')

    s = np.loadtxt("data.txt")
    points = [[]]
    j = 0
    for i in range(len(s)):
        if (s[i] == -1):
            points.append([])
            j+=1
        else:
            points[j].append(s[i])
    print(len(points))
    endpoint_idx = 0
    displaypoints = [[[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]]]
    for pointlist in points:
        ax1.clear()
        ax1.imshow(a.pathPlanner.entropyMaps[endpoint_idx]._distribution, interpolation='nearest')
        ax2.clear()
        ax2.imshow(a.maps[1]._distribution, interpolation='nearest')
        ax3.clear()
        ax3.imshow(a.maps[2]._distribution, interpolation='nearest')
        ax1.title.set_text('Entropy')
        ax2.title.set_text('Shade')
        ax3.title.set_text('Risk')
        for i in range(0,len(pointlist), 2):
            displaypoints[i//2][0].append(pointlist[i])
            displaypoints[i//2][1].append(pointlist[i+1])
        for i in range(10):
            endpoint = a.pathPlanner.endpoints[endpoint_idx]
            ax1.plot(displaypoints[i][0], displaypoints[i][1], 'r', linewidth=1)
            ax2.plot(displaypoints[i][0], displaypoints[i][1], 'r', linewidth=1)
            ax3.plot(displaypoints[i][0], displaypoints[i][1], 'r', linewidth=1)
            ax1.title.set_text('Entropy')
            ax2.title.set_text('Shade')
            ax3.title.set_text('Risk')
            if len(displaypoints[i][0]) > 0:
                if np.abs(endpoint[0] - displaypoints[i][0][-1]) < 3 and np.abs(endpoint[1] - displaypoints[i][1][-1]) < 3:
                    print("FOUND ENDPOINT")
                    endpoint_idx += 1
                circ1 = Circle((displaypoints[i][0][-1],displaypoints[i][1][-1]),1,ec='red',fc='red')
                circ2 = Circle((displaypoints[i][0][-1], displaypoints[i][1][-1]), 1, ec='red', fc='red')
                circ3 = Circle((displaypoints[i][0][-1], displaypoints[i][1][-1]), 1, ec='red', fc='red')
                ax1.add_artist(circ1)
                ax2.add_artist(circ2)
                ax3.add_artist(circ3)
        if (live):
            plt.show(block=False)
            plt.pause(0.00000000001)
    print("gets to display")
    plt.show()



def displayPathsProbandCoarseReconstructed(next, live):
    (a, i, j, k, l, o) = next
    keep_fraction = 0.035
    sf = np.loadtxt("saved data/agents/a.txt")
    sensorFootprints = [[], [], [], [], [], [], [], [], [], []]
    for i in range(len(sf)):
        if (sf[i] != -1):
            sensorFootprints[i].append(sf[i])
    print(sensorFootprints)
    for x in sensorFootprints:
        if len(x) == 0:
            x.append(1.0)
    s = np.loadtxt("saved data/paths/data.txt")
    points = [[]]
    j = 0
    for i in range(len(s)):
        if (s[i] == -1):
            points.append([])
            j += 1
        else:
            points[j].append(s[i])
    print(len(points))
    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.set_aspect('equal')
    ax2.set_aspect('equal')
    ax2.imshow(a.map._distribution)
    displaypoints = [[[], []], [[], []], [[], []], [[], []], [[], []], [[], []], [[], []], [[], []], [[], []], [[], []]]
    for pl in range(len(points)):
        pointlist = points[pl]
        '''ma = infoMaps[pl // 50]
        map = np.array(ma)
        for i in range(len(map)):
            map[i] = np.array(ma[i])'''
        map_fft = fftpack.fft2(a.map._distribution)
        r,c = map_fft.shape
        map_fft[int(r * keep_fraction):int(r * (1 - keep_fraction))] = 0
        map_fft[:, int(c * keep_fraction):int(c * (1 - keep_fraction))] = 0
        map_fft[0:int(r * keep_fraction), 0:int(c * keep_fraction)] = 0
        ax1.clear()
        ax2.clear()
        ax1.imshow(fftpack.ifft2(map_fft).real)
        ax2.imshow(a.map._distribution)
        for i in range(0, len(pointlist), 2):
            displaypoints[i // 2][0].append(pointlist[i])
            displaypoints[i // 2][1].append(pointlist[i + 1])
        for i in range(10):
            ax1.plot(displaypoints[i][0], displaypoints[i][1])
            ax2.plot(displaypoints[i][0], displaypoints[i][1])
            if len(displaypoints[i][0]) > 0:
                circ1 = Circle((displaypoints[i][0][-1], displaypoints[i][1][-1]), int(sensorFootprints[i][0]),
                               ec='pink', fc='none')
                circ2 = Circle((displaypoints[i][0][-1], displaypoints[i][1][-1]), int(sensorFootprints[i][0]),
                               ec='pink', fc='none')
                ax1.add_artist(circ1)
                ax2.add_artist(circ2)
        if (live):
            plt.show(block=False)
            plt.pause(0.00000000001)
    plt.show()


'''def displayPathsonTerrain(next, live):
    (a,i,j,k,l,o) = next
    plt.imshow(a.map._terrainDistribution)
    plt.pause(1)
    s = np.loadtxt("saved paths/data.txt")
    points = [[]]
    j = 0
    for i in range(len(s)):
        if (s[i] == -1):
            points.append([])
            j+=1
        else:
            points[j].append(s[i])
    print(len(points))
    displaypoints = [[[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]]]
    for pointlist in points:
        for i in range(0,len(pointlist), 2):
            displaypoints[i//2][0].append(pointlist[i])
            displaypoints[i//2][1].append(pointlist[i+1])
        plt.imshow(a.map._terrainDistribution)
        for i in range(10):
            plt.plot(displaypoints[i][0], displaypoints[i][1])
        if (live):
            plt.show(block=False)
            plt.pause(0.00000000001)
    plt.show()

def displayPathsonBoth(next, live):
    (a,i,j,k,l,o) = next
    #colors = ["brown", "blue", "green"]
    fig = plt.figure(figsize=(8,4))
    maps = [a.map._terrainDistribution, a.map._distribution]
    plots = []
    plt.pause(1)
    for i in range(2):
        plots.append(fig.add_subplot(1,2,i+1))
        plots[-1].set_title("Map " + str(i))
        plt.imshow(maps[i])
    plt.pause(1)
    s = np.loadtxt("saved paths/data.txt")
    points = [[]]
    j = 0
    for i in range(len(s)):
        if (s[i] == -1):
            points.append([])
            j+=1
        else:
            points[j].append(s[i])
    print(len(points))
    displaypoints = [[[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]]]
    for pointlist in points:
        for i in range(0,len(pointlist), 2):
            displaypoints[i//2][0].append(pointlist[i])
            displaypoints[i//2][1].append(pointlist[i+1])
        for i in range(2):
            plt.imshow(maps[i])
        for i in range(10):
            for n in range(2):
                plots[n].plot(displaypoints[i][0], displaypoints[i][1])
        if (live):
            plt.show(block=False)
            plt.pause(0.00000000001)
    plt.show()'''

def displaySub(next, live):
    (a,i,j,k,l,o) = next
    fig,ax = plt.subplots(1)
    ax.set_aspect('equal')
    ax.imshow(a.map._distribution)
    print(type(a.map._distribution))
    plt.pause(10)
    UAV = Image.open('UAV.png')
    UAV.resize((15,15))
    #UAV = np.asarray(UAV)
    UAV = OffsetImage(UAV)
    destroyer = Image.open('destroyersmall.png')
    destroyer.resize((10,30))
    #destroyer = np.asarray(destroyer)
    destroyer = OffsetImage(destroyer)
    sub = Image.open('subsmall.png')
    sub.resize((20, 60))
    sub = OffsetImage(sub)
    #UAV = OffsetImage(plt.imread('UAV.png'))
    #destroyer = OffsetImage(plt.imread('destroyer.png'))
    sf = np.loadtxt("saved data/agents/a.txt")
    sensorFootprints = [[],[],[],[],[],[],[],[],[],[]]
    for i in range(len(sf)):
        if (sf[i] != -1):
            sensorFootprints[i].append(sf[i])
    print(sensorFootprints)
    for x in sensorFootprints:
        if len(x) == 0:
            x.append(1.0)

    s = np.loadtxt("saved data/paths/data.txt")
    points = [[]]
    j = 0
    for i in range(len(s)):
        if (s[i] == -1):
            points.append([])
            j+=1
        else:
            points[j].append(s[i])
    print(len(points))
    displaypoints = [[[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]], [[],[]]]
    for pointlist in points:
        ax.clear()
        ax.imshow(a.map._distribution)
        #ab1 = AnnotationBbox(sub, (50, 50), frameon=False)
        #ax.add_artist(ab1)
        for i in range(0,len(pointlist), 2):
            displaypoints[i//2][0].append(pointlist[i])
            displaypoints[i//2][1].append(pointlist[i+1])
        for i in range(10):
            ax.plot(displaypoints[i][0], displaypoints[i][1])
            #if len(displaypoints[i][0]) > 0:
                #if (int(sensorFootprints[i][0]) > 5):
                    #ab = AnnotationBbox(UAV, (displaypoints[i][0][-1], displaypoints[i][1][-1]), frameon=False)
                #else:
                    #ab = AnnotationBbox(destroyer, (displaypoints[i][0][-1], displaypoints[i][1][-1]), frameon=False)
                #ax.add_artist(ab)
                #circ = Circle((displaypoints[i][0][-1],displaypoints[i][1][-1]),int(sensorFootprints[i][0]),ec='pink',fc='none')
                #ax.add_artist(circ)
        if (live):
            plt.show(block=False)
            plt.pause(0.00000000001)
    plt.show()

def runDisplay(taskList, displayType):
    if (displayType == 0):
        displayPathsonProbability(taskList[0], True)
    elif (displayType == 1):
        displayPathsonTerrain(taskList[0], True)
    elif (displayType == 2):
        displayPathsonBoth(taskList[0], True)
    elif (displayType == 3):
        displayInfoMaps(taskList[0])
    elif (displayType == 4):
        displayPathsonInfoandProbability(taskList[0], True)
    elif (displayType == 5):
        displayPathsProbandCoarseReconstructed(taskList[0], True)
    elif (displayType == 6):
        displaySub(taskList[0], True)
    else:
        displayGaussians(taskList[0])