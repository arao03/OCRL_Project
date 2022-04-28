import numpy as np
from matplotlib import pyplot as plt

class RiskCost:
    """A class that takes in a path to numpy array of slopes and allows for calls on a function that returns the cost at that location"""

    def __init__(self, path_to_slopes="../data/cuprite_slope.npy"):
        """Initializes the class with a path to numpy array of slopes"""
        self.slopes = np.load(path_to_slopes)
        self.cost = np.zeros(self.slopes.shape)
        self.inflated_cost = np.zeros(self.slopes.shape)

        window = 2 # window size for calculating inflated cost
        thresh = 45 # threshold for inflating cost
        inflate_scalar = 10 # scalar for inflating cost
        for i in range(self.slopes.shape[0]):
            for j in range(self.slopes.shape[1]):
                # set cost as slope value
                self.cost[i,j] = self.slopes[i,j] 

                
                # set inflated cost as the maximum of the surrounding costs if above threshold
                i_bottom = max(0, min(i-window, self.slopes.shape[0]))
                i_top = max(0, min(i+window, self.slopes.shape[0]))
                j_left = max(0, min(j-window, self.slopes.shape[1]))
                j_right = max(0, min(j+window, self.slopes.shape[1]))
                inflate_cost = 0
                if np.amax(self.slopes[i_bottom:i_top, j_left:j_right]) >= thresh:
                    inflate_cost = np.amax(self.slopes[i_bottom:i_top, j_left:j_right])*inflate_scalar
                self.inflated_cost[i,j] = inflate_cost

        print("gets here")
        np.savetxt('risk_map.txt', self.inflated_cost[1070:1270,1070:1270])
                
    def get_cost(self, x, y):
        """Returns the cost at a given location"""
        return self.cost[x, y]
    
    def get_inflated_cost(self, x, y):
        """Returns the inflated cost at a given location"""
        return self.inflated_cost[x, y]

risk = RiskCost()
# Display cost map
plt.imshow(risk.inflated_cost, cmap='hot', interpolation='nearest')
plt.show()
plt.imshow(risk.inflated_cost[1070:1270,1070:1270], cmap='hot', interpolation='nearest')
plt.show()

