# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 19:19:04 2024

@author: UX3402

All you need to change is DataFolder filepath

File Strucutre:
DataFolder/
    ->SpecFolder/
        ->spec1.spe
        ->spec2.spe
        ->spec1.txt (if SPEtoTXT(DataFolder) executed)
        ->spec2.txt (if SPEtoTXT(DataFolder) executed)
    ->PowermeterData.txt (Should be only .txt file)
    ->SpotVis.png
    ->CutAndGlue.png
    ->CutAndGlue.spe
    ->...
"""

import os
from glob import glob
import numpy as np
from SPE_Converter import SPEtoTXT
import matplotlib.pyplot as plt  
from scipy import integrate, optimize

DataFolder = "/Users/maxbehrens/OneDrive - UAM/Proyecto de grado/Data/data_for_saturation_curve/"
#root = "C:/Users/EQUIPO/Desktop/HBN scanner/Saturation Curve/Saturation-curve-data-C1-2024-10-07/"

convert_SPE = input("Do you need to convert SPE data to TXT (y/n): ")
background_check = input("Do you want to take into account background noise, you must have a background data file(y/n): ")
method = int(input("What method do you want to use 1 = use maximas, 2 = integrate, 3 = both, 4 = none: "))


#Turns all SPE files to TXT files with the following information on the first 9 lines
#SPE version
#Frame width
#Frame height
#No. of frames
#Exposure (s)
#Laser Wavelength (nm)
#Central Wavelength (nm)
#Date collected
#Time collected (hhmmss))
if convert_SPE == "y":
    SPEtoTXT(DataFolder)

"""
File preparation for saturation curves
"""
# creates array of all data files ending with txt
SpecFolder = glob(DataFolder + "/*/")[0] 
TXTFileList = glob(SpecFolder + "*.txt")
if len(glob(DataFolder + "*.txt")) == 1:
    PowerFile = glob(DataFolder + "*.txt")[0] #Only text file in main folder is power meter file
else:
    print('Error: Make sure there is only 1 TXT file and that it contains PowerMeter data')

#To sort list of files in ascending power order
TXT_order_list = []
for path in TXTFileList:
    file_name = os.path.basename(path).split('/')[-1]
    file_name = file_name[:12]
    power = ''.join(filter(lambda i: i.isdigit(), file_name))
    TXT_order_list.append(int(power))
sorted = np.argsort(TXT_order_list)
OrderedTXTFileList = []
for i in sorted:
    OrderedTXTFileList.append(TXTFileList[i])
   
#Finding index at which the maxima is centred around
maxima_index = []
for doc in OrderedTXTFileList:
        try:
            wav, count = np.loadtxt(doc, delimiter='\t', skiprows=10, unpack = True) #To skip headers
            arg_max = np.argmax(count)  # Encuentra el máximo de los counts
            maxima_index.append(arg_max)
        except Exception as e:
                print(f"Error al leer {doc}: {e}")
maxima_index.sort()
centre_index = round(np.mean(maxima_index[3:-3]))

#To easily plot a spectrum
#wav, count = np.loadtxt(OrderedTXTFileList[0], delimiter='\t', skiprows=10, unpack=True)
#plt.plot(wav, count)
#plt.show()

#Getting power data 
power = np.loadtxt(PowerFile)

"""
Calculating Saturation Curve
"""
guess = [100000, 3] #For curve-fit
xdata = np.linspace(min(power), max(power), 100)
def sat_fit(P, Imax, Psat):
        return Imax / (1 + Psat / P)

maxima_values = []
integral_values = []
for doc in OrderedTXTFileList:
    try:
        wav, count = np.loadtxt(doc, delimiter='\t', skiprows=10, unpack = True) #To skip headers
        if method == 1 or method == 3:
            #Maxima method
            m = max(count[centre_index - 120:centre_index + 120])  #Find maximum of counts +-10nm around centre wavelength (~12 points/nm)
            maxima_values.append(m)
        if method == 2 or method == 3:
            #Integral method
            centre = np.argmax(count[centre_index - 120:centre_index + 120]) + 120 #Find centre of peak
            m = integrate.simpson(count[centre - 120:centre + 120]) #Integrate +-10nm around centre
            integral_values.append(m)
    except Exception as e:
                print(f"Error al leer {doc}: {e}")

"""
Plotting Saturation Curve
"""     
if method == 1 or method == 3:
    print("Maxima Values: ", maxima_values)

    popt, pcov = optimize.curve_fit(sat_fit, power, maxima_values, p0 = guess)
    print("Imax, Psat:", popt)
    
    plt.plot(xdata, sat_fit(xdata, *popt), label = "Fit")
    plt.plot(power, maxima_values, "x", label = "Data")
    plt.title("Saturation curve using maxima's")
    plt.grid()
    plt.legend()
    plt.xlabel("Power (mW)")
    plt.ylabel("Counts")
  

if method == 2 or method == 3:
    print("Area Values: ", integral_values)
    
    popt, pcov = optimize.curve_fit(sat_fit, power, integral_values, p0 = guess)
    print("Imax, Psat:", popt)
    
    plt.plot(xdata, sat_fit(xdata, *popt), label = "Fit")
    plt.plot(power, integral_values, "x", label = "Data")
    plt.title("Saturation curve using areas's")
    plt.grid()
    plt.legend()
    plt.xlabel("Power (mW)")
    plt.ylabel("Counts")
    plt.show()
            
