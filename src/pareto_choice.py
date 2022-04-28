import numpy as np


def pareto_choices(costs):
    """
    Find the pareto-efficient points
    :param costs: An (n_points, n_costs) array
    :return: A (n_points, ) boolean array, indicating whether each point is Pareto efficient
    """
    is_efficient = np.ones(costs.shape[0], dtype = bool)
    for i, c in enumerate(costs):
        is_efficient[i] = np.all(np.any(costs[:i]>c, axis=1)) and np.all(np.any(costs[i+1:]>c, axis=1))
    return is_efficient

# test
'''costs = np.array([[1, 2, 2],
                  [2, 2, 0],
                  [1, 3, 2],
                  [6, 2, 2]])
print(pareto_choices(costs))
'''