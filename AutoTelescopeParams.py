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
def QFunc(z, zr, w0, lamda):
    Rfunc = z + zr*zr/z
    Wfunc = w0 * np.sqrt(1 + (z/zr) * (z/zr))
    denom = complex(1/Rfunc, - lamda / (np.pi * Wfunc * Wfunc))
    return 1 / denom

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
    return np.array([[1,x],[0,1]])

def LensM(f1):
    """Lens

    Args:
        f1: Focal length
    """
    return np.array([[1,0],[-1/f1, 1]])

def M21(d1, f1):
    output = np.matmul(LensM(f1), FreeSpaceM(d1))
    return output

def M321(d1, f1, d2):
    output = np.matmul(FreeSpaceM(d2)), M21(f1, d1)
    return output

def M4321(d1, f1, d2, f2):
    output = np.matmul(LensM(f2), M321(d1, f1, d2))
    return output

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
x_val = np.linspace(0, max(dist))

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

""" 
Finding evolution of gaussian beam
"""
# Distances between lenses (to be optimised)
d1 = 1.0 # Distance from x = 0 to first lens
d2 = 0.1 # Distance from first lens to second lens
d3 = 2.0 # Distance between collimators (d3 > d1 + d2)



    









