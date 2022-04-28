from primitive import BasePrimitive
from math import sin, cos, atan2, pi
import mathlib

class PrimitiveCurve(BasePrimitive):


    def __init__(self, time, speed, point, heading, radius, dir):
        self._heading = heading
        self._time = time
        self._speed = speed
        self._point = point
        self._radius = radius
        self._dir = dir

    def getAngleFromCenterToStart(self):
        (cx, cy) = self.getCircleCenter()
        (x,y) = self.getStartPoint()
        return (atan2( y - cy, x - cx) + 2*pi) % (2*pi)

    def getAngleFromCenterToEnd(self):
        (cx, cy) = self.getCircleCenter()
        (x, y) = self.getEndPoint()
        return (atan2( y - cy, x - cx) + 2*pi) % (2*pi)

    def getCircleCenter(self):
        (x,y) = self._point
        rx = -cos(self._heading + pi/2) * self._radius
        ry = sin(self._heading + pi/2) * self._radius
        s = -self._dir

        return(rx*s + x, ry*s + y)

    def isLooping(self):
        return self._time * self._speed > self._radius * 2 * pi

    def isInMapBounds(self, map):
#        pointsToCheck = []
        (xc,yc) = self.getCircleCenter()
        r = self._radius
        pointsToCheck = [(xc + r, yc),(xc, yc + r),(xc-r,yc),(xc, yc-r)]
#        if self.isLooping():
#            r = self._radius
#            pointsToCheck = [(xc + r, yc),(xc, yc + r),(xc-r,yc),(xc, yc-r)]
#        else:
#            pointsToCheckLocal = mathlib.pointsToCheck(self.getAngleFromCenterToStart(),
#                                                       self.getAngleFromCenterToEnd(),
#                                                       self._radius, -self._dir)
#            for point in pointsToCheckLocal:
#               pointsToCheck.append((point[0] + xc, point[1] + yc))
        for point in pointsToCheck:
            if map.isWorldPointOutOfBounds(point):
                return False
        return True


    def getPointAtTime(self, time):
        ''' Return a point that we would reach by travelling on the primitive
                    in time time. If

                        Args:
                            time     (float): travel time, should be between
                '''
        L = (self._speed*time)
        r = self._radius
        ang = self._heading
        (x,y) = self._point
        s = -self._dir
        # coordinates are flipped on map (pygame standard), so we do -sin()
        xc = - r*sin(ang - s*(L/r)) + r*sin(ang)
        yc = - r*cos(ang - s*(L/r)) + r*cos(ang)
        return (s*xc + x, s*yc + y)

    def getHeadingAtTime(self, time):
        ''' Returns a float from 0 to 2pi corresponding to the heading at a given time.

                        Args:
                            time    (float): time to check heading for
        '''
        L = (self._speed * time)
        r = self._radius
        ang = self._heading
        s = -self._dir

        xc = s*r*sin(ang - s*(L/r))
        yc = s*r*cos(ang - s*(L/r))

        return atan2(-s*yc, s*xc) + pi/2
