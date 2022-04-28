from pathprimitive import PathPrimitive
import abc


class PathGenerator:

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    @abc.abstractmethod
    def generateRandomPrimitivePath(self, map, agent):
        return (PathPrimitive([]), True)
