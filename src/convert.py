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

'''data = np.loadtxt('../data/entropy_upsampled.txt')
#data = data/np.max(data)
for i in range(200):
    for j in range(200):
        if data[i,j] < 0:
            data[i,j] = 0
print(np.average(data))
plt.imshow(data)
plt.show()
np.savetxt('../data/new_entropy_upsampled.txt', data)'''

data1 = np.loadtxt('../data/new_entropy_upsampled.txt')

data2 = np.loadtxt('../data/new_shade_map.txt')

data3 = np.loadtxt('../data/new_risk_map.txt')

fig, (ax1, ax2, ax3) = plt.subplots(1,3)
ax1.set_aspect('equal')
ax2.set_aspect('equal')
ax3.set_aspect('equal')
ax1.imshow(data1, interpolation='nearest')
ax2.imshow(data2, interpolation='nearest')
ax3.imshow(data3, interpolation='nearest')
ax1.title.set_text('Entropy')
ax2.title.set_text('Shade')
ax3.title.set_text('Risk')
plt.show()


'''data = np.loadtxt('../data/shade_map.txt')
data = data/np.max(data)
print(np.average(data))
plt.imshow(data)
plt.show()

np.savetxt('../data/new_shade_map.txt', data)
'''