import matplotlib.pyplot as plt
import numpy as np
import cv2
from matplotlib.patches import Circle

traj = np.loadtxt('../logs/trajectory1.txt')
img = cv2.imread('../data/terrain.png')
map = img[:300,:300,:]
fig, ax = plt.subplots(1)
ax.set_aspect('equal')
ax.imshow(map)
'''displaypoints = [[],[]]
for i in range(0, len(traj), 2):
    displaypoints[0].append(traj[i])
    displaypoints[1].append(traj[i + 1])'''
#for point in traj:
    #ax.clear()
    #ax.imshow(img)
    #print(point)
ax.plot(traj[:,0], traj[:,1], 'r', linewidth=2)
circ = Circle((traj[-1][0], traj[-1][1]), 2, ec='red', fc='red')
ax.add_artist(circ)
plt.show()
