import os
import numpy as np
import matplotlib.pyplot as plt

def findMultipleIntensityMax(XYint,XYcoord,XYorder): 
    sensitivity = 0.8 # fraction of the brightest spot we want to pick up
    # finding maximas
    a = np.pad(XYint, (1, 1),
            mode='constant',
            constant_values=(0,0)) # adds 0 to the edges of the array to avoid errros
    loc_max = []
    rows = a.shape[0]
    cols = a.shape[1]
    for ix in range(1, rows - 1):
        for iy in range(1, cols - 1):
            if a[ix, iy] > a[ix, iy + 1] and a[ix, iy] > a[ix, iy - 1] and \
            a[ix, iy] > a[ix + 1, iy] and a[ix, iy] > a[ix + 1, iy - 1] and \
            a[ix, iy] > a[ix + 1, iy + 1] and a[ix, iy] > a[ix - 1, iy] and \
            a[ix, iy] > a[ix - 1, iy - 1] and a[ix, iy] > a[ix - 1, iy + 1] and \
            a[ix, iy] > sensitivity * biggest_brightness:
                loc_max.append([ix-1,iy-1])
    print('Maximum at indexs:', loc_max)
    maxPos = []
    for indices in loc_max:
        i = indices[0]
        j = indices[1]
        index=int(XYorder[i,j]-1)
        XmaxPos=XYcoord[index,0]
        YmaxPos=XYcoord[index,1]
        maxPos.append([XmaxPos, YmaxPos])
    return np.array(maxPos)

'''
To plot heatmap with maxima of data taken already'''
# initialising paramters (distances are in nm)
filepath = os.getcwd() + '/Data/data_for_maxima_location/'
filename = '2024_7_29_10_26_21_ROIscan.txt'
sensitivity = 0.8 # fraction of the brightest spot we want to pick up
stepsize = 250
Xdist = 8000
Ydist = 8000

# loading in data
data = np.loadtxt(filepath + filename, skiprows=1, delimiter=',', dtype=float)
biggest_brightness = np.amax(data)

# Convert steps to distance
distance_x = data.shape[1] * stepsize  # Total distance in x direction
distance_y = data.shape[0] * stepsize  # Total distance in y direction

a = np.pad(data, (1, 1),
            mode='constant',
            constant_values=(0,0)) # adds 0 to the edges of the array to avoid errros
loc_max = []
rows = a.shape[0]
cols = a.shape[1]
for ix in range(1, rows - 1):
    for iy in range(1, cols - 1):
        if a[ix, iy] > a[ix, iy + 1] and a[ix, iy] > a[ix, iy - 1] and \
        a[ix, iy] > a[ix + 1, iy] and a[ix, iy] > a[ix + 1, iy - 1] and \
        a[ix, iy] > a[ix + 1, iy + 1] and a[ix, iy] > a[ix - 1, iy] and \
        a[ix, iy] > a[ix - 1, iy - 1] and a[ix, iy] > a[ix - 1, iy + 1] and \
        a[ix, iy] > sensitivity * biggest_brightness:
            loc_max.append([ix-1,iy-1])
print('Maximum at indexs:', loc_max)

fig, ax = plt.subplots(1,1)
ax.set_xlabel('Distance (nm)')
ax.set_ylabel('Distance (nm)')
im = ax.imshow(data,cmap='magma',extent=[0, distance_x, 0, distance_y],vmax=None)

# Create colorbar
cbar = ax.figure.colorbar(im, ax=ax)
cbar.ax.set_ylabel('Single counts', rotation=-90, va="bottom")

for i in range(len(loc_max)):
    x_coord = (loc_max[i][1] + 0.5) * stepsize
    y_coord = (data.shape[0] - loc_max[i][0] - 0.5) * stepsize  
    ax.plot(x_coord, y_coord, 'x', color = 'black')

plt.show()