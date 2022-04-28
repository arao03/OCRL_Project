
from path import Path
from primitive import BasePrimitive

class PathPrimitive(Path):

    def __init__(self, path):
        self.primitiveList = path

    def getTotalTime(self):
        totalTime = 0.0
        for primitive in self.primitiveList:
            totalTime += primitive.getTotalTime()
        return totalTime

    def getPointAtTime(self, time):
        timeLeft = time
        for primitive in self.primitiveList:
            if(timeLeft < 0.0):
                return primitive.getEndPoint()
            if(timeLeft < primitive.getTotalTime()):
                return primitive.getPointAtTime(timeLeft)
            else:
                timeLeft -= primitive.getTotalTime()
        return (0.0, 0.0)

    def getHeadingAtTime(self, time):
        timeLeft = time
        for primitive in self.primitiveList:
            if (timeLeft < 0.0):
                return primitive.getEndHeading()
            if (timeLeft < primitive.getTotalTime()):
                return primitive.getHeadingAtTime(timeLeft)
            else:
                timeLeft -= primitive.getTotalTime()
        return 0.0
