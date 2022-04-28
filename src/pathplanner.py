import operator
import math
from map import Map
import numpy as np
import mathlib
from agent import Agent

class PathPlanner:


    def __init__(self,map,gaussianMap):
        self.map = map
        self.gaussianMap = gaussianMap


    def _clamp(self,list1,n):
        """ Clamps list1 to length n
            Args:
                list1   ((int,int) list): the path to clamp
                n       (int): length to clamp to
        """
        newlist = [list1[0]]
        listx = [x[0] for x in list1]
        listy = [x[1] for x in list1]
        i=1
        while(i<len(list1)):
            dist = math.sqrt((listx[i]-listx[i-1])**2+(listy[i]-listy[i-1])**2)
            if n>=dist:
                n=n-dist
                newlist.append(list1[i])
                if n==0:
                    return newlist
            else:
                frac = n/dist
                x = listx[i-1]+(listx[i]-listx[i-1])*frac
                y = listy[i-1]+(listy[i]-listy[i-1])*frac
                newlist.append((round(x),round(y)))
                return newlist
            i=i+1
        return newlist

    def getPath(self, startpoint, m, numPoint, len):
        """ Returns a random path using m distribution
                Args:
                    startpoint  ((int,int)): the point from which we generate the path
                    m           (Map): map
                    n           (int): Number of points to generate
                    len         (int): length of the path
        """
        path=[(int,int)]*(numPoint+1)
        path[0]=startpoint
        for a in range(1,numPoint+1):
            path[a] = m.getRandomPoint()
        return self._clamp(path,len)

    def getYPath(self, startpoint, m, n, len):
        """ Returns a path using m distribution with points sorted by Y
                Args:
                    startpoint  ((int,int)): the point from which we generate the path
                    m           (Map): map
                    n           (int): Number of points to generate
                    len         (int): length of the path
        """

        list = self.getPath(startpoint, m, n, len)
        list.sort(key=operator.itemgetter(1))
        return list

    def getXPath(self, startpoint, m, n, len):
        """ Returns a path using m distribution with points sorted by X
                Args:
                    startpoint  ((int,int)): the point from which we generate the path
                    m           (Map): map
                    n           (int): Number of points to generate
                    len         (int): length of the path
        """
        list = self.getPath(startpoint, m, n, len)
        list.sort(key=operator.itemgetter(0))
        return list

    def closestPointPath(self, startpoint, m, numPoint, leng):
        """ Returns a path using the closest local minimum algorithm
                Args:
                    startpoint  ((int,int)): the point from which we generate the path
                    m           (Map): map
                    numPoint    (int): Number of points to generate
                    leng        (int): length of the path
        """
        path = [(int, int)] * (numPoint + 1)
        path[0] = startpoint
        for a in range(1, numPoint+1):
            path[a] = m.getRandomPoint()
        listx = [x[0] for x in path]
        listy = [x[1] for x in path]
        superiorPath = []
        min = 100000
        min_index = -1
        cur = 0
        superiorPath.append(path[0])

        for j in range(numPoint):
            for i in range(len(path)):
                dist = math.sqrt((listx[i] - listx[cur]) ** 2 + (listy[i] - listy[cur]) ** 2)
                if i!=cur and dist < min:
                    min = dist
                    min_index = i
            superiorPath.append(path[min_index])
            del path[cur]
            del listx[cur]
            del listy[cur]

            if cur < min_index:
                cur = min_index-1
            else:
                cur = min_index
            min = 100000

        return self._clamp(superiorPath,leng)


    def pathInfoMap(self, pointsList, map, gaussianMap):
        """
        This function returns an information map obtained by the robot. It is a 2D array with the same size as the stochastic map.
        Args:
            pointsList (list): a list of all points (x, y) along the randomly generated path
            map (list): 2D array - the stochastic map from map.py
            gaussianMap (list): 2D array that represents robot's field of vision
        """

        infoMap = np.zeros((len(map), len(map)))

        x_coord = [x[0] for x in pointsList]
        y_coord = [x[1] for x in pointsList]
        vision = len(gaussianMap)
        points = len(pointsList)

        for i in range(points):
            for j in range (0, vision):
                for k in range (0, vision):
                    vx = x_coord[i] + j - vision//2
                    vy = y_coord[i] + k - vision//2
                    if vx >= 0 and vx < len(map) and vy >= 0 and vy < len(map[0]):
                        infoMap[vx][vy] += gaussianMap[j][k] * map[vx][vy]

        sum = 0
        for a in range(0, len(map)):
            for b in range(0, len(map[0])):
                sum = sum + infoMap[a][b]
        return infoMap/sum

    def getBestPath(self, startpoint, m, n, len, tries=3):
        """ Returns the best path out of multiple tries
        Args:
            startpoint  ((int,int)): the point from which we generate the path
            m           (Map): map to generate path on
            n           (int): number of points to generate
            len         (int): length of generated path
            tries       (int): how many paths should be sampled
        """
        minErg = -1
        bestPath = np.array([])
        for i in range(tries):
            list = self.closestPointPath(startpoint, m, n, len)
            pathDistrib = self.pathInfoMap(mathlib.makeAllLineWithSpeed(list,3), self.map.getDistribution(), self.gaussianMap)
            pathDistrib = pathDistrib/pathDistrib.sum()
            erg = mathlib.calcErgodicity(self.map, pathDistrib, 10)
            if minErg < 0 or erg < minErg:
                minErg = erg
                bestPath = list
        return bestPath


    def getBestPathWithObstacles(self, startpoint, m, n, leng, tries,obstacleMap):
        """ Returns the best path out of multiple tries
        Args:
            startpoint  ((int,int)): the point from which we generate the path
            m           (Map): map to generate path on
            n           (int): number of points to generate
            len         (int): length of generated path
            tries       (int): how many paths should be sampled
        """
        minErg = -1
        bestPath = np.array([])
        for i in range(tries):
            list = self.getPathWithObstacle(startpoint, m, n, leng, obstacleMap)
            pathDistrib = self.pathInfoMap(mathlib.makeAllLineWithSpeed(list,3), self.map.getDistribution(), self.gaussianMap)
            erg = mathlib.calcErgodicity(self.map, pathDistrib, 10)
            if minErg < 0 or erg < minErg:
                minErg = erg
                bestPath = list
        return bestPath

    def getPathWithObstacle(self, startpoint, m, n, leng, obstacleMap):
        path = [startpoint]
        a=0
        prev = startpoint
        while(a<n):
            point = m.getRandomPoint()
            list1 = mathlib.makeLineH(prev[0],prev[1],point[0],point[1],2)
            #print(list1)
            isGood = True
            for b in range(0, len(list1)):
                if(not obstacleMap[list1[b][0]][list1[b][1]]):
                    isGood=False
                    a=a-1
                    break
            if(isGood):
                path.append(point)
                prev=point
            #print(isGood)
            a=a+1


        return self._clamp(path,leng)



    def multiPath(self, m, n, leng, numAgent, oMap):
        """ Returns a list of paths, each of one robot
        Args:

        """
        multilist = []
        for i in range(numAgent):
            a = Agent((len(m._distribution)*i//numAgent,0))
            list = self.getPathWithObstacle(a.startPt, m, n, leng, oMap)
            multilist.append(list)
        return multilist

    def multiAgentInfoMap(self, multilist, numAgent, map):
        """Returns the information map after multiple agents search the area
        Args:
        """
        multimap = np.zeros((len(map._distribution), len(map._distribution)))
        for i in range(numAgent):
            onemap = self.pathInfoMap(mathlib.makeAllLineWithSpeed(multilist[i],3), self.map.getDistribution(), self.gaussianMap)
            for j in range(len(onemap)):
                for k in range(len(onemap)):
                    multimap[j][k] += onemap[j][k]
        return multimap/numAgent

    def bestMultiPath(self, m, n, len, tries, numAgent, oMap):
        minErg = -1
        multiPath = []
        for i in range(tries):
            multilist = self.multiPath(m, n, len, numAgent,oMap)
            pathDistrib = self.multiAgentInfoMap(multilist, numAgent, m)
            erg = mathlib.calcErgodicity(self.map, pathDistrib, 10)
            if minErg < 0 or erg < minErg:
                minErg = erg
                multiPath = multilist
        return multiPath

    def bestMultiPathWithSpeed(self,m,n,time,tries,agents,omap):
        minErg = -1
        multipath = []
        for i in range(tries):
            tempmultipath = []
            for j in range(len(agents)):
                agents[j].path=self.getPathWithObstacleWithSpeed(agents[j],m,n,time,omap)
                tempmultipath.append(agents[j].path)
            pathDistrib = self.multiAgentInfoMapWithSpeed(tempmultipath,agents,m)
            erg = mathlib.calcErgodicity(self.map, pathDistrib, 10)
            if minErg < 0 or erg < minErg:
                minErg = erg
                multipath = tempmultipath
                for agent in agents:
                    agent.bestspeedlist=agent.speedlist
        return multipath

    def pathInfoMapWithSpeed(self,pl, agent, map):
        infoMap = np.zeros((len(map), len(map)))

        pointsList = mathlib.makeAllLineWithSpeed(pl,1)

        x_coord = [x[0] for x in pointsList]
        y_coord = [x[1] for x in pointsList]
        vision = len(agent.visionmap)
        speedindex = -1

        for i in range(len(pointsList)):
            if pl[speedindex][0]==x_coord[i] and pl[speedindex][1]==y_coord[i]:
                speedindex = speedindex + 1
            if (i%agent.normspeed)==0:
                for j in range (0, vision):
                    for k in range (0, vision):
                        vx = x_coord[i] + j - vision//2
                        vy = y_coord[i] + k - vision//2
                        if vx >= 0 and vx < len(map) and vy >= 0 and vy < len(map[0]):
                            infoMap[vx][vy] += agent.visionmap[j][k] * map[vx][vy]*agent.normspeed/agent.speedlist[speedindex]

        sum = 0
        for a in range(0, len(map)):
            for b in range(0, len(map[0])):
                sum = sum + infoMap[a][b]
        return infoMap/sum

    def multiAgentInfoMapWithSpeed(self, multilist, agents, map):
        """Returns the information map after multiple agents search the area
        Args:
        """
        multimap = np.zeros((len(map._distribution), len(map._distribution)))
        for i in range(len(agents)):
            onemap = self.pathInfoMapWithSpeed(multilist[i],agents[i], self.map.getDistribution())
            for j in range(len(onemap)):
                for k in range(len(onemap)):
                    multimap[j][k] += onemap[j][k]
        return multimap/len(agents)

    def getPathWithObstacleWithSpeed(self, agent, m, n, time, obstacleMap):
        path = [agent.startPt]
        a=0
        prev = agent.startPt
        while(a<n):
            point = m.getRandomPoint()
            list2 = mathlib.makeLineH(prev[0],prev[1],point[0],point[1],2)
            #print(list1)
            isGood = True
            for b in range(0, len(list2)):
                if(not obstacleMap[list2[b][0]][list2[b][1]]):
                    isGood=False
                    a=a-1
                    break
            if(isGood):
                path.append(point)
                prev=point
            #print(isGood)
            a=a+1

        agent.speedlist = mathlib.getRandomSpeedList(n,agent.minspeed,agent.normspeed,agent.maxspeed)

        return self._speedclamp(path,time,agent.speedlist)

    def _speedclamp(self,list1,n,speedlist):
        newlist = [list1[0]]
        listx = [x[0] for x in list1]
        listy = [x[1] for x in list1]
        i = 1
        while (i < len(list1)):
            time = math.sqrt((listx[i] - listx[i - 1]) ** 2 + (listy[i] - listy[i - 1]) ** 2) / speedlist[i-1]
            if n >= time:
                n = n - time
                newlist.append(list1[i])
                if n == 0:
                    return newlist
            else:
                frac = n / time
                x = listx[i - 1] + (listx[i] - listx[i - 1]) * frac
                y = listy[i - 1] + (listy[i] - listy[i - 1]) * frac
                newlist.append((round(x), round(y)))
                return newlist
            i = i + 1
        return newlist

