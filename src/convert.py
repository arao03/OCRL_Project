import numpy as np
from matplotlib import pyplot as plt

'''
data = np.load('entropy_upsampled.npy')
print(data.shape)
print(data)
np.savetxt('entropy_upsampled.txt', data)

data = np.load('entropy_upsampled.npy')
print(data.shape)
np.savetxt('entropy_upsampled.txt', data)
'''

#data = np.loadtxt("entropy_upsampled.txt")
#print(data)

'''data = np.loadtxt('../data/risk_map.txt')
print(np.average(data))
plt.imshow(data)
plt.show()
for i in range(200):
    for j in range(200):
        if data[i,j] == 0:
            data[i,j] = 1
        else:
            data[i,j] = (1000 - data[i,j])/1000


plt.imshow(data)
plt.show()

np.savetxt('../data/new_risk_map.txt', data)
'''

data = np.loadtxt('../data/entropy_upsampled.txt')
#data = data/np.max(data)
for i in range(200):
    for j in range(200):
        if data[i,j] < 0:
            data[i,j] = 0
print(np.average(data))
plt.imshow(data)
plt.show()
np.savetxt('../data/new_entropy_upsampled.txt', data)


'''data = np.loadtxt('../data/shade_map.txt')
data = data/np.max(data)
print(np.average(data))
plt.imshow(data)
plt.show()

np.savetxt('../data/new_shade_map.txt', data)
'''