''' Base class for storing map information. Every map has a specified size and a probability
    distribution for each cell on the map that sum up to 1. Think of it as a slightly more complicated
    2D float array.

    Every map has map coordinates that correspond to cells in the 2D array used for the map distribution and
    world coordinates that correspond to the actual world position of an object in the map. Map coordinates
    are used to  get probabilities in given cells, world positions to get distances between objects etc.
    You can convert between the two with functions in the map. The positions of all entities are in world coordinates
    so you need to convert them to map coordinates to get the cell a given entity is on.
'''

import numpy as np
import mathlib
import math


class Map:
    '''Object representing 2D stochastic map of probabilities.
        Attributes:
            sizeX             (int): size of the map in the x-axis
            sizeY             (int): size of the map in the x-axis
            _distribution     (2D floats array): 2D stochastic array containing
                                                all the probabilities
                                                for the map
            _cumulativeDistribution (2D float array): cumulative version of
                                                      the _distribution array
            dX                 (float): the length in x of a single cell (in metres)
            dY                 (float): the length in y of a single cell (in metres)
    '''

    def __init__(self, sizeX=100, sizeY=100, dX=1, dY=1, gaussSize=50, d = np.ones((100,100))):
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.dX = dX
        self.dY = dY
        self._distribution = d  #mathlib.makeGaussian(sizeX, sizeY, gaussSize)
        self._distribution /= self._distribution.sum();
        self._cumulativeDistribution = self._calculateCumulativeDistribution(self._distribution)

    def _calculateCumulativeDistribution(self, distrib):
        '''Calculates the cumulative distribution based on the actual distribution

            Args:
                distrib     (2D float array): 2D stochastic array corresponding
                                              to the probabilty distribution

        '''
        cumul = np.zeros((len(distrib), len(distrib[0])))
        for i in range(len(distrib)):
            for j in range(len(distrib[i])):
                if i == 0 and j == 0:
                    cumul[i][j] = distrib[i][j]
                else:
                    index = i*len(distrib[i]) + j
                    prevIndex = index - 1;
                    prevIndices = divmod(prevIndex, len(distrib[i]))
                    cumul[i][j] = distrib[i][j] + cumul[prevIndices[0]][prevIndices[1]]
        return cumul

    def isWorldPointOutOfBounds(self, point):
        (x,y) = point
        return x < 0 or x > self.sizeX*self.dX or y < 0 or y > self.sizeY*self.dY

    def getWorldScaleArrays(self):
        ''' Returns a tuple of float arrays representing
        '''
        xr = np.arrange(0, self.sizeX * self.dX, self.dX)
        yr = np.arrange(0, self.sizeY * self.dY, self.dY)
        return (xr, yr)

    def getWorldSize(self):
        ''' Returns a tuple of floats representing the size of the world the map represents
        '''
        return (self.sizeX * self.dX, self.sizeY * self.dY)

    def getDistribution(self):
        ''' Returns the probability distribution array of the map
        '''
        return self._distribution

    def h(self, i):
        return (i // self.sizeX, i % self.sizeX)

    def getRandomPoint(self):
        '''Returns a random point chosen using the probability array
        '''
        r = np.random.uniform()
        cumul = self._cumulativeDistribution
        if (r <= cumul[0][0]):
            return (0, 0)
        lo = 0
        hi = self.sizeX * self.sizeY - 1
        while (lo < hi - 1):
            mid = (lo + hi) // 2
            (i, j) = self.h(mid)
            if (cumul[i][j] >= r):
                hi = mid
            else:
                lo = mid

        return self.h(hi)

    def getPointProbability(self, x, y):
        '''Returns the probability of point at positions x and y

            Args:
                x       (int): x coordinate of the point
                y       (int): y coordinate of the point
        '''
        if(x < 0 or y < 0 or x >= len(self._distribution) or y >= len(self._distribution[x])):
            return 0
        else:
            return self._distribution[x][y]

    def getAvgPointProbability(self):
        ''' Returns avg probability of points in the map

        '''
        return self._distribution.sum() / (self.sizeX * self.sizeY)

    def updateMapDistribution(self, distribution):
        ''' Changes the map's distribution

            Args:
                distribution    (2D float array): the new distribution
        '''
        self._distribution = distribution
        self.sizeX = len(distribution)
        self.sizeY = len(distribution[0])
        self._cumulativeDistribution = self._calculateCumulativeDistribution(self._distribution)

    def worldToMap(self, worldX, worldY):
        ''' Returns (int,int) a point corresponding to a point in the map closest to the world x and y

                Args:
                    worldX      (float): the world x position
                    worldY      (float): the world y position
        '''
        return (int(round(worldX / self.dX)), int(round(worldY / self.dY)))

    def mapToWorld(self, mapX, mapY):
        ''' Returns (float, float) a point corresponding to a point in the world closest to the map x and y

                        Args:
                            mapX      (int): the map x position
                            mapY      (int): the map y position
        '''
        return (mapX*self.dX, mapY*self.dY)

    def addDistribToMap(self, distrib, center, normalize = True):
        '''Adds the given distribution to our map
            Args:

                distrib          - 2D float array: distribution to add
                center           - (int,int): the point at which the center of distrib should be when adding
                normalize        - bool: should the map be renormalized after adding
        '''
        for vX in range(0, len(distrib)):
            for vY in range(0, len(distrib[0])):
                mapX = center[0] + vX - len(distrib) // 2
                mapY = center[1] + vY - len(distrib[0]) // 2
                if mapX >= 0 and mapX < len(self.getDistribution()) and mapY >= 0 and mapY < len(self.getDistribution()[0]):
                    self._distribution[mapX][mapY] = max(0, min( 1, self._distribution[mapX][mapY] + distrib[vX][vY] ))
        if normalize:
            self._distribution / self._distribution.sum();
        self._cumulativeDistribution = self._calculateCumulativeDistribution(self._distribution)

