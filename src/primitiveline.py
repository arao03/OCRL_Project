from primitive import BasePrimitive
from math import sin, cos

class PrimitiveLine(BasePrimitive):


    def __init__(self, time, speed, point, heading):
        self._heading = heading
        self._time = time
        self._speed = speed
        self._point = point

    def isInMapBounds(self, map):
        return map.isWorldPointOutOfBounds( self.getStartPoint() ) == False and \
               map.isWorldPointOutOfBounds(self.getEndPoint()) == False

    def getPointAtTime(self, time):
        ''' Return a point that we would reach by travelling on the primitive
                    in time time. If

                        Args:
                            time     (float): travel time, should be between
                '''
        dist = (self._speed*time)
        (x,y) = self._point
        # coordinates are flipped on map (pygame standard), so we do -sin()
        return (x + dist*cos(self._heading), y - dist*sin(self._heading))

    def getHeadingAtTime(self, time):
        ''' Returns a float from 0 to 2pi corresponding to the heading at a given time.

                        Args:
                            time    (float): time to check heading for
        '''
        return self._heading
