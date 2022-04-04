import numpy as np

class RiskCost:
    """A class that takes in a path to numpy array of slopes and allows for calls on a function that returns the cost at that location"""

    def __init__(self, path_to_slopes="data/cuprite_slope.npy"):
        """Initializes the class with a path to numpy array of slopes"""
        self.slopes = np.load(path_to_slopes)
        self.cost = np.zeros(self.slopes.shape)
        for i in range(self.slopes.shape[0]):
            for j in range(self.slopes.shape[1]):
                self.cost[i,j] = self.slopes[i,j] 
        

    def get_cost(self, x, y):
        """Returns the cost at a given location"""
        return self.cost[x, y]

    def get_cost_array(self):
        """Returns the cost array"""
        return self.cost

    def get_slope_array(self):
        """Returns the slope array"""
        return self.slopes

