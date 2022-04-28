import numpy as np
import math
import random


def calcErgodicity(infoMap, pathDistrib, splitMapMode=0, precision=15 ):
    ''' returns the ergodicity of the pathDistrib in relation to the infoMap
        Args:
            infoMap         (Map): Map representing the information distribution
            pathDistrib     (2D float array): The distribution representing the path info gained
            precision       (int): how precise the calculation should be
    '''
    mapDim = (infoMap.sizeX, infoMap.sizeY)
    mapDeltas = (infoMap.dX, infoMap.dY)
    fourierInfo = np.real(np.fft.fft2(infoMap.getDistribution()))
    centralFFT = 5

    if( splitMapMode == 1 ):
        for i in range(-50, 50):
            for j in range(-50, 50):
                if (i < -centralFFT or i > centralFFT - 1) \
                        and (j < -centralFFT or j > centralFFT - 1):
                    fourierInfo[j][i] = 0
    if( splitMapMode == 2 ):
        for i in range(-50, 50):
            for j in range(-50, 50):
                if (i >= -centralFFT and i <= centralFFT - 1) \
                        and (j >= -centralFFT and j <= centralFFT - 1):
                    fourierInfo[j][i] = 0


    fourierPath = np.real(np.fft.fft2(pathDistrib))
    ergodMetric = 0
    for kX in range(precision):
        for kY in range(precision):
            lambdaK = 1.0 / ((1.0 + (kX * kX) + (kY * kY)) ** 1.5)
            ergodMetric += (lambdaK*((fourierInfo[kX][kY]) - fourierPath[kX][kY]) ** 2)

    return ergodMetric

def calcFourierCoeff(distrib, mapDim, mapDeltas, precision=10):
    ''' calculates the fourier coefficients for the given distribution
        Args:
            distrib     (2D float array): distribution to get coefficients for
            mapDim      ((int, int): Dimensions of the map grid
            mapDeltas   ((float, float)): Local to World factors for grid
            precision   (int): How precise the calculation should be (i.e. size of fourier matrix)
    '''
    (mapSizeX, mapSizeY) = mapDim
    (dX, dY) = mapDeltas
    fourierCoeffs  = np.zeros((precision, precision))
    hk = math.sqrt(mapSizeX *dX * mapSizeY *dY)

    for fX in range(precision):
        for fY in range(precision):

            for cntX in range(mapSizeX):
                for cntY in range(mapSizeY):
                    mcx = math.cos(fX * math.pi * (cntX / mapSizeX))
                    mcy = math.cos(fY * math.pi * (cntY / mapSizeY))
                    fourierCoeffs[fX][fY] += distrib[cntX][cntY] * mcx * mcy

            hkt = hk
            if fX != 0:
                hkt *= 0.5
            if fY != 0:
                hkt *= 0.5
            fourierCoeffs[fX][fY] /= hkt

    return fourierCoeffs


def calcFourierCoeffFast(distrib, mapDimensions, mapDeltas, Nkx=10, Nky=10):

    fourierCoeffs = np.zeros((Nkx, Nky))
    (mapSizeX, mapSizeY) = mapDimensions
    (dX, dY) = mapDeltas
    Lx = mapSizeX * dX
    Ly = mapSizeY * dY
    X = np.array([[dX * x for x in range(mapSizeX)] for y in range(mapSizeY)])
    Y = np.array([[dY * y for x in range(mapSizeX)] for y in range(mapSizeY)])

    temp = np.matrix((np.append([1], math.sqrt(0.5) * np.matrix(np.ones((1, Nky - 1))))))
    HK = np.multiply(math.sqrt(Lx * Ly), temp.T * temp)
    distrib = np.reshape(distrib, X.shape, 'F')

    for kx in range(0, Nkx):
        for ky in range(0, Nky):
            fourierCoeffs[kx, ky] = (np.matrix(
                np.multiply(np.multiply(distrib, np.cos(kx * math.pi * X / Lx)), np.cos(ky * math.pi * Y / Ly)))).sum() / HK[ky, kx]

    return fourierCoeffs



def makeGaussian(sizeX, sizeY, fwhm=3, center=None, normalize=True):
    """
    Make a rectangular gaussian kernel.
    Args:
            size       ((int,int)): is the width and height of the
            normalize  (bool): should all values in distribution sum up to 1
            fwhm       (int): is full-width-half-maximum, which
                              can be thought of as an effective radius.
            center     ((int,int)): the center of the gaussian distribution
    Example: makeGaussian((5,3)false,2,[2,2])
    """

    list = np.zeros((sizeX, sizeY))

    if center is None:
        x0 = sizeX // 2
        y0 = sizeY // 2
    else:
        x0 = center[0]
        y0 = center[1]

    for x in range(sizeX):
        for y in range(sizeY):
            list[x][y] = np.exp(-4 * np.log(2) * ((x - x0) ** 2 + (y - y0) ** 2) / fwhm ** 2)

    return (list / list.sum()) if normalize else list


def round(x):
    """
    Round a float to its nearest int
    Args:
            x    (float): value to round
    """
    return math.floor(x+0.5)

def makeLine(x1, y1, x2, y2):
    """
    This function takes in two points (x1,y1) and (x2, y2) and returns a list of points on the line
    The number of points depends on the length of the line

    Args:
        x1 (int): the x value of the first point
        y1 (int): the y value of the first point
        x2 (int): the x value of the second point
        y2 (int): the y value of the second point
    """
    dist = math.sqrt((x1-x2)**2 +(y1-y2)**2)
    numPoint = round(dist)-1;
    list = [(x1, y1), (x2, y2)]
    if numPoint == 0:
        return list
    ux = (x1-x2)/numPoint
    uy = (y1-y2)/numPoint
    for a in range(1,numPoint-1):
        list.insert(a,(round(x1-a*ux),round(y1-a*uy)))
    return list

def makeLineH(x1, y1, x2, y2, h):
    """
    This function takes in two points (x1,y1) and (x2, y2) and returns a list of points on the line
    The number of points depends on the length of the line

    Args:
        x1 (int): the x value of the first point
        y1 (int): the y value of the first point
        x2 (int): the x value of the second point
        y2 (int): the y value of the second point
    """
    dist = math.sqrt((x1-x2)**2 +(y1-y2)**2)
    numPoint = round(dist)*h-1;
    list = [(x1, y1), (x2, y2)]
    if numPoint <= 0:
        return list
    ux = (x1-x2)/numPoint
    uy = (y1-y2)/numPoint
    for a in range(1,numPoint-1):
        list.insert(a,(round(x1-a*ux),round(y1-a*uy)))
    return list

def makeAllLine(list1):
    """
    Given a list of endPoints, returns a list of all points on the path using makeLine

     Args:
         list1 (list): the list of endpoints
    """
    list2=list()
    listx = [x[0] for x in list1]
    listy = [x[1] for x in list1]
    for a in range(0,len(list1)-1):
        if len(list2)>0:
            del list2[-1]
        list2.extend(makeLine(listx[a],listy[a],listx[a+1],listy[a+1]))
    return list2

def makeAllLineWithSpeed(list1,speed):
    """ Returns a set of points that is obtained by going over a path defined by list1 in speed sized steps.

        Args:
            list1       (list): the path from which the points will be gotten
            speed       (int): size of the steps to get the points


    """
    list2 = makeAllLine(list1)
    newlist = [list2[0]]
    i=speed
    while i < len(list2):
        newlist.append(list2[i])
        i=i+speed
    return newlist


def getRandomSpeedList(num,min,std,max):
    list1 = []

    for a in range(num):
        list1.append(random.random()*(max-min)+min)

    return list1

def quadrant(angle):
    if 0 <= angle and angle < math.pi / 2:
        return 1
    elif math.pi / 2 <= angle and angle < math.pi:
        return 2
    elif math.pi <= angle and angle < 3*math.pi/2:
        return 3
    else:
        return 4

def polarToRect(angle, rad):
    return (rad*math.cos(angle),rad*math.sin(angle))

def pointsToCheck(startpointangle, endpointangle, radius, direction): #Do not feed loops into this
    qs = quadrant(startpointangle)
    qe = quadrant(endpointangle)
    if qs==qe:
        if startpointangle < endpointangle:
            if direction > 0:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius)]
            else:
                return [(0,radius), (radius, 0), (-radius, 0), (0, -radius)]
        else:
            if direction > 0:
                return [(0,radius), (radius, 0), (-radius, 0), (0, -radius)]
            else:
                return [polarToRect(startpointangle,radius),polarToRect(endpointangle,radius)]
    elif qs==1:
        if qe==2:
            if direction > 0:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (0,radius)]
            else:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (radius,0), (0, -radius), (-radius, 0)]
        elif qe==3:
            if direction > 0:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (0, radius), (-radius, 0)]
            else:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (radius, 0), (0, -radius)]
        elif qe==4:
            if direction > 0:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (0, radius), (0, -radius), (-radius, 0)]
            else:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (radius, 0)]
    elif qs==2:
        if qe==3:
            if direction > 0:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (-radius, 0)]
            else:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (radius,0), (0, -radius), (0, radius)]
        elif qe==4:
            if direction > 0:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (0, -radius), (-radius, 0)]
            else:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (radius, 0), (0, radius)]
        elif qe==1:
            if direction > 0:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (radius,0), (0, -radius), (-radius, 0)]
            else:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (0, radius)]
    elif qs==3:
        if qe==4:
            if direction > 0:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (0, -radius)]
            else:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (radius,0), (-radius, 0), (0, radius)]
        elif qe==1:
            if direction > 0:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (0, -radius), (radius, 0)]
            else:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (-radius, 0), (0, radius)]
        elif qe==2:
            if direction > 0:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (radius,0), (0, -radius), (0, radius)]
            else:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (-radius, 0)]
    elif qs==4:
        if qe==1:
            if direction > 0:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (radius, 0)]
            else:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (0, radius), (0, -radius), (-radius, 0)]
        elif qe==2:
            if direction > 0:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (0, radius), (radius, 0)]
            else:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (-radius, 0), (0, -radius)]
        elif qe==3:
            if direction > 0:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (0, radius), (0, -radius), (radius, 0)]
            else:
                return [polarToRect(startpointangle, radius), polarToRect(endpointangle, radius), (-radius, 0)]




