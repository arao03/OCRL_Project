import numpy as np 
import cv2
from matplotlib import pyplot as plt

src_file = "../data/cuprite_dem.npy"  # Get from the Drive folder

data = np.load(src_file)
data = data[:, :, 0]  # Get rid of that pesky last dimension

def shadowTrace(map, sun_angle = np.deg2rad(45), sun_direction = "+X", map_size = 1000):
    """
          Simulates a sun location and generates shade from the elevation map.
        This takes an angle to the sun and rotates the elevation map accordingly.
        Then it checks if each pixel is at the highest elevation for the remainder 
        of the map.

        Assumes that the Sun is to the right, for convenience.

        Arguments:
          - map:         2D map with each element corresponding to the height at that location        |  [L x W]
          - sun_angle:   Angle to the sun                                                             |  Scalar 
          - map_size:    The distance spanned by the image along the direction towards the sun        |  Scalar 

        Returns:
          - shadeMap:    2D mask with '0'/'1' corresponding to areas in shade/sun                     |  [L x W]

    """
    # Allow Top, Right, Left, and Bottom ?

    elevMap = np.copy(map)
    L, W = elevMap.shape


    # # # Super efficient and vectorized code for raytracing # # #

    # Rotate the elevation map by the angle to the sun
    if sun_direction == "+X":
        pixel_size = map_size / W   # Determine the length of each pixel (in meters I guess...?)
        dist_from_far_edge = np.arange(W) * pixel_size   # How far away (m) each pixel is from side furthest from the sun
    elif sun_direction == "-X":
        pixel_size = map_size / W   
        dist_from_far_edge = np.flip(np.arange(W)) * pixel_size   
    elif sun_direction == "+Y":
        pixel_size = map_size / L  
        dist_from_far_edge = np.arange(L) * pixel_size  
    elif sun_direction == "-Y":
        pixel_size = map_size / L  
        dist_from_far_edge = np.flip(np.arange(L)) * pixel_size  
    else:
        print("ERROR - Please enter valid map direction!")
        return None


    # Determine how much to increase each pixels height by based off of the sun's position
    height_offset_per_row = dist_from_far_edge * np.tan(-sun_angle)  # Negative to rotate everything the correct direction

    # Update each pixel of the elevation map
    if (sun_direction == "+X") or (sun_direction == "-X"):
        elevMap += np.tile(height_offset_per_row, (L, 1))
    else:
        elevMap += np.tile(height_offset_per_row, (W, 1)).T

    shadeMap = np.zeros(elevMap.shape)
    for u in range(L):
        if (u % 50 == 0):
            print("{} out of {}".format(u, L))
        for v in range(W):

            # Check if each cell is the largest in the remainder of the row
            z = elevMap[u, v]

            try: 
                if sun_direction == "+X":
                    remaining_row_max = np.max(elevMap[u, v:])  # Maximum for the remainder of the row 
                elif sun_direction == "-X":
                    remaining_row_max = np.max(elevMap[u, :v])
                elif sun_direction == "+Y":
                    remaining_row_max = np.max(elevMap[u:, v])
                else: # "-Y"
                    remaining_row_max = np.max(elevMap[:u, v])
            except:
                remaining_row_max = 0.0
            if (z < remaining_row_max):
                continue
            else:
                shadeMap[u, v] = 1  # NO shade here

    return shadeMap


def randomShadePatch(pic):
    """
        Generates random clouds of shade. Apparently this is not really useful
    """

    L, W = pic.shape
    minDim = L if L < W else W
    numPatches = np.random.randint(5, 30)

    shadeMap = np.ones(pic.shape)

    for i in range(numPatches):
        # Define center 
        x0, y0 = np.random.randint(0, L), np.random.randint(0, W)
        patchSize = np.random.randint(1, minDim // 10)

        minX, maxX = x0 - patchSize, x0 + patchSize 
        minY, maxY = y0 - patchSize, y0 + patchSize 

        # Clip at edges
        if minX < 0:
            minX = 0 
        if minY < 0:
            minY = 0
        if maxX >= L:
            maxX = L 
        if maxY >= W:
            maxY = W

        shadeMap[minX:maxX, minY:maxY] = 0

    return cv2.GaussianBlur(shadeMap, (201, 201), 100)


# Show the image
plt.imshow(data[:, :], cmap = "gray")
plt.show()

# Generate the shade mask
shade = shadowTrace(data)
plt.imshow(data, cmap = "gray")
plt.show()

#plt.imshow(np.loadtxt('entropy_upsampled.txt'))

# Mask the image
data[shade < 0.5] = 0
plt.imshow(data)
plt.show()

np.savetxt('../data/new_shade_map.txt', data[1070:1270,1550:1750])

print("Done")