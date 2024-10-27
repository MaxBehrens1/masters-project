""" 
Code will automatically find optimal paramters to couple light between single mode optical fibers
All distance is in meters
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

""" 
Defining necessary functions and variables
"""
def QuadFit(z, d0, z0, zr):
    """Fit of gaussian beam

    Args:
        z: Distance
        d0: Minimum beam width
        z0: Position of minimum beam width
        zr: Rate of beam expansion

    Returns:
        _type_: _description_
    """
    return d0 * np.sqrt(1 + (z-z0)/zr * (z-z0)/zr)

# Transfer matrices free space and lenses
def FreeSpaceM(x):
    """Free space

    Args:
        x: Distance
    """
    return [[1,x],[0,1]]

def LensM(f1):
    """Lens

    Args:
        f1: Focal length
    """
    return [[1,0],[-1/f1, 1]]

wavelength = 650e-9


""" 
Calculating complex beam parameter using given data
"""
# Beam widths (wA/wB) and given distance from collimator (dist)
dist = np.array([0.005, 0.32, 0.67, 1.225, 1.76]) 
wA = np.array([1730.45, 1456, 1389.4, 1580.9, 1856]) * 1e-6
wB = np.array([1729.4, 1477.3, 1450.95, 1702.05, 1851.45]) * 1e-6

# Finds optimal paramteres
paramsB, covB = curve_fit(QuadFit, dist, wA)
paramsC, covC = curve_fit(QuadFit, dist, wB)
x_val = np.linspace(0, max(dist), 500)

qA = complex(-paramsB[1],paramsB[2])
qB = complex(-paramsC[1],paramsC[2])

# Plots the beam width evolution
fig, axs = plt.subplots(2)
#wA
axs[0].set_title("wA")
axs[0].plot(x_val, QuadFit(x_val, *paramsB), label = "Fit")
axs[0].plot(dist, wA, 'x', label = f"q={qA:.4f}")
axs[0].grid()
axs[0].legend()
axs[0].set(xlabel = "Distance (m)", ylabel = "Beam width (m)")
axs[0].set_ylim(0, max(wA) + 0.1 * max(wA))
#wB
axs[1].set_title("wB")
axs[1].plot(x_val, QuadFit(x_val, *paramsC), label = "Fit")
axs[1].plot(dist, wB, 'x', label = f"q={qB:.4f}")
axs[1].grid()
axs[1].legend()
axs[1].set(xlabel = "Distance (m)", ylabel = "Beam width (m)")
axs[1].set_ylim(0, max(wB) + 0.1 * max(wB))
fig.tight_layout()
plt.show()

print(f"qA={qA}, qB={qB}")

""" 
Finding evolution of gaussian beam
"""
# Distances between lenses (to be optimised)
d1 = 0.45 # Distance from x = 0 to first lens
d2 = 0.075 # Distance from first lens to second lens
d3 = 0.64 # Distance between collimators (d3 > d1 + d2)
f1 = 0.035 # Focal length of lens 1
f2 = 0.04 # Focal length of lens 2
# Creating variable x for each section
allx = np.linspace(0, d3, 500)
x1 = np.linspace(0, d1, 500)
x2 = np.linspace(d1, d1+d2, 500)
x3 = np.linspace(d1+d2, d3, 500)

M1 = FreeSpaceM(x1)
M1D = FreeSpaceM(d1)
M2 = LensM(f1)
M3 = FreeSpaceM(x2 - d1)
M3D = FreeSpaceM(d2)
M4 = LensM(f2)
M5 = FreeSpaceM(x3 - (d1 + d2))
M21 = np.matmul(M2, M1D)
M321 = np.matmul(M3D, M21)
M4321 = np.matmul(M4, M321)

q1 = (M1[0][0] * qA + M1[0][1]) / (M1[1][0] * qA + M1[1][1])
q2 = (M21[0][0]* qA + M21[0][1]) / (M21[1][0] * qA + M21[1][1])
q3 = (M3[0][0] * q2 + M3[0][1]) / (M3[1][0] * q2 + M3[1][1])
q4 = (M4321[0][0]* qA + M4321[0][1]) / (M4321[1][0] * qA + M4321[1][1])
q5 = (M5[0][0] * q4 + M5[0][1]) / (M5[1][0] * q4 + M5[1][1])
qout = qB + d3 - allx

g1 = np.sqrt(-wavelength / (np.pi * (1/q1).imag)) # Path from x=0 to lens 1
g2 = np.sqrt(-wavelength / (np.pi * (1/q3).imag)) # Path from lens 1 to lens 2
g3 = np.sqrt(-wavelength / (np.pi * (1/q5).imag)) # Path from lens 2 to inf.
g4 = np.sqrt(-wavelength / (np.pi * (1/qout).imag)) # Path from recieving collimator

plt.plot(x1, g1, color = "grey")
plt.plot(x1, -g1, color = "grey")
plt.plot(x2, g2, color = "grey")
plt.plot(x2, -g2, color = "grey")
plt.plot(x3, g3, color = "grey")
plt.plot(x3, -g3, color = "grey")
plt.plot(allx, g4, color = "red")
plt.plot(allx, -g4, color = "red")
plt.show()
