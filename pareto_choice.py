import numpy as np

# returns the Pareto optimal choice from a list of rewards
def pareto_choice(rewards_list):
    best_set = rewards_list[0]
    for i in range(len(rewards_list)):
        if np.all(rewards_list[i] >= best_set):
            best_set = rewards_list[i]
    return best_set

# test
rewards = []
rewards.append(np.array([1, 2, 2]))
rewards.append(np.array([1, 3, 2]))
rewards.append(np.array([6, 2, 2]))
print(pareto_choice(rewards))