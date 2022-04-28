

class Path():
    '''Base class for all paths. All coordinates in path are in world space'''

    def getTotalTime(self):
        ''' gets the total time required to traverse path
        :return:    (float) time to traverse path
        '''
        return 0.0

    def getPointAtTime(self, time):
        ''' gets the point on the path after travelling for time seconds
        :param time: (float) time in seconds to get point for
        :return: ((float,float)) the point on the path
        '''
        return (0.0, 0.0)

    def getHeadingAtTime(self, time):
        ''' gets the heading on the path after travelling for time seconds
        :param time: (float) time in seconds to get heading for
        :return: (float) the heading on path
        '''
        return 0.0

