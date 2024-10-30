""" 
Code will automatically find optimal paramters to couple light between single mode optical fibers
All distance is in meters
The further apart of the couplers, the worse coupling efficiency

Constraints:
*First lens is minimum dmin meters away from first collimator
*The two lenses are at least 0.02 meters apart
*The second lens is at least 0.05 meters away from the second collimator
"""
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, minimize


"""
CHANGE DATA FOR YOUR EXPERIMENT
"""
focal_lengths = [0.035, 0.04, 0.05, 0.06, 0.075] # List of possible lens combinations
dmin = 0.6 # Minimum distance from collimator to first lens in m
d3 = 0.85 # Distance between collimators (d3 > d1 + d2) in m
wavelength = 650e-9 # Wavelength of laser used

# Beam widths (wA/wB) and given distance from collimator (dist)
dist = np.array([0.005, 0.32, 0.67, 1.225, 1.76]) 
wA = np.array([1730.45, 1456, 1389.4, 1580.9, 1856]) * 1e-6
wB = np.array([1729.4, 1477.3, 1450.95, 1702.05, 1851.45]) * 1e-6

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

def Calcg(d1, d2, d3, f1, f2, qA, qB, wavelength):
    allx = np.linspace(0, d3)
    x1 = np.linspace(0, d1)
    x2 = np.linspace(d1, d1+d2)
    x3 = np.linspace(d1+d2, d3)

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
    qout = qB - (allx - d3)
    qideal = qB - (x3 - d3)

    g1 = np.sqrt(-wavelength / (np.pi * (1/q1).imag)) # Path from x=0 to lens 1
    g2 = np.sqrt(-wavelength / (np.pi * (1/q3).imag)) # Path from lens 1 to lens 2
    g3 = np.sqrt(-wavelength / (np.pi * (1/q5).imag)) # Path from lens 2 to collimator
    g4 = np.sqrt(-wavelength / (np.pi * (1/qout).imag)) # Path from recieving collimator
    gideal = np.sqrt(-wavelength / (np.pi * (1/qideal).imag)) # Path from recieving collimator between collimator and lens 2
    
    return allx, x1, x2, x3, g1, g2, g3, g4, gideal

def MSE(vec1, vec2):
    return np.sum((vec1 - vec2)**2) / (len(vec1))

def FuncOptim(dvec, f1, f2, qA, qB, wavelength):
    allx, x1, x2, x3, g1, g2, g3, g4, gideal = Calcg(dvec[0], dvec[1], d3, f1, f2, qA, qB, wavelength)
    current_mse = MSE(gideal, g3)
    return current_mse

""" 
Calculating complex beam parameter using given data
"""
# Finds optimal paramteres
paramsA, covA = curve_fit(QuadFit, dist, wA)
paramsB, covB = curve_fit(QuadFit, dist, wB)
x_val = np.linspace(0, max(dist))

qA = complex(-paramsA[1],paramsA[2])
qB = complex(-paramsB[1],paramsB[2])

# Plots the beam width evolution
fig, axs = plt.subplots(2)
#wA
axs[0].set_title("wA")
axs[0].plot(x_val, QuadFit(x_val, *paramsA), label = "Fit")
axs[0].plot(dist, wA, 'x', label = f"q={qA:.4f}")
axs[0].grid()
axs[0].legend()
axs[0].set(xlabel = "Distance (m)", ylabel = "Beam width (m)")
axs[0].set_ylim(0, max(wA) + 0.1 * max(wA))
#wB
axs[1].set_title("wB")
axs[1].plot(x_val, QuadFit(x_val, *paramsB), label = "Fit")
axs[1].plot(dist, wB, 'x', label = f"q={qB:.4f}")
axs[1].grid()
axs[1].legend()
axs[1].set(xlabel = "Distance (m)", ylabel = "Beam width (m)")
axs[1].set_ylim(0, max(wB) + 0.1 * max(wB))
fig.tight_layout()
plt.show()

print(f"qA={qA}, qB={qB}")

""" 
Finding evolution of gaussian beam. Time for "ML" ;)
"""
tolerance = 1e-25
bound = [[dmin, d3], [0.02, d3/2]]

best_mse = [0,0,0,0,10] # Array of [f1, f2, d1, d2, MSE]
for i in range(len(focal_lengths)):
    for j in range(i+1, len(focal_lengths)):
        f1 = focal_lengths[i]
        f2 = focal_lengths[j]
        for _ in tqdm(range(100), desc=f"[f1,f2]={[f1,f2]}"):
            guess = [np.random.rand() * (d3 - dmin) + dmin, np.random.rand() * d3/2 + 0.01]
            optimal_min = minimize(FuncOptim, x0=guess, args=(f1, f2, qA, qB, wavelength), bounds=bound, tol=tolerance)
            if optimal_min.x[0] + optimal_min.x[1] < d3 - 0.05 and (optimal_min.fun < best_mse[4]):
                best_mse = [f1, f2, optimal_min.x[0], optimal_min.x[1], optimal_min.fun]

mses = np.array(best_mse)
dvector = [mses[2], mses[3]]
f1 = mses[0]
f2 = mses[1]

print(f"[f1, f2, d1, d2, MSE] = {mses}")

allx, x1, x2, x3, g1, g2, g3, g4, gideal = Calcg(dvector[0], dvector[1], d3, f1, f2, qA, qB, wavelength)
plt.plot(dvector[0], 0, "|", alpha = 0.9, markersize = 300, color = "black")
plt.plot(dvector[1] + dvector[0], 0, "|", alpha = 0.9, markersize = 300, color = "black")
plt.plot(x1, g1, color = "grey")
plt.plot(x1, -g1, color = "grey")
plt.plot(x2, g2, color = "grey")
plt.plot(x2, -g2, color = "grey")
plt.plot(x3, g3, color = "grey")
plt.plot(x3, -g3, color = "grey")
plt.plot(allx, g4, color = "red")
plt.plot(allx, -g4, color = "red")
plt.text(0.1,0.5, f'Lens Parameters:\n*f1={f1}m, d1={dvector[0]:.4f}m \n*f2={f2}m, d2={dvector[1]:.4f}m',
         ha="left", va="center", transform=plt.gca().transAxes)
plt.show()

