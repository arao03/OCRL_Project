import abc


class BasePrimitive():
    __metaclass__ = abc.ABCMeta

    def getTimeFit(self, time):
        '''Given a time, returns 0 if time fits in the curve's
            time bounds (i.e. between 0 and self._time). Otherwise returns
            the difference between time and self_time.

                Args:
                    time        (float): time to check for
        '''
        return 0 if (time >= 0 and time <= self._time)  else (time - self._time)

    def getTotalTime(self):
        return self._time

    @abc.abstractmethod
    def getPointAtTime(self, time):
        ''' Return a point that we would reach by travelling on the primitive
            in time time. If

                Args:
                    time     (float): travel time, should be between
        '''
        return

    def getEndPoint(self):
        ''' Returns (float, float) the point at which the primitive ends.
        '''
        return self.getPointAtTime(self._time)

    def getStartPoint(self):
        ''' Returns (float, float) the point at which the primitive starts.
         '''
        return self._point

    @abc.abstractmethod
    def getHeadingAtTime(self, time):
        ''' Returns a float from 0 to 2pi corresponding to the heading at a given time.

                Args:
                    time    (float): time to check heading for
         '''
        return

    @abc.abstractmethod
    def isInMapBounds(self, map):
        return

    def getInitialHeading(self):
        ''' Returns a float from 0 to 2pi corresponding to the heading at the start of the primitive
        '''
        return self._heading

    def getEndHeading(self):
        ''' Returns a float from 0 to 2pi corresponding to the heading at the end of the primitive
        '''
        return self.getHeadingAtTime(self._time)

    def getSpeed(self):
        ''' Returns speed primitive is travelled with.
        '''
        return self._speed