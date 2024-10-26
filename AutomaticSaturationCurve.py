# -*- coding: utf-8 -*-
"""
File to automatically run a saturation curve

It will create a new file in: C:\Users\EQUIPO\Desktop\HBN scanner\Saturation Curve

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
import time 
import sys
import datetime 
from tqdm import tqdm

#To convert SPE to CSV
try:
    sys.path.append("C:/Users/EQUIPO/Desktop/HBN scanner/QOSS/Scanner")
    import SPE_Converter as SPE
except:
    print("Failed to import SPE_Converter")

#LightField Imports
import clr
from System import String
from System.Collections.Generic import List

from System.IO import *

sys.path.append(os.environ.get('LIGHTFIELD_ROOT'))
sys.path.append(os.environ.get('LIGHTFIELD_ROOT')+'//AddInViews')
clr.AddReference('PrincetonInstruments.LightFieldViewV5')
clr.AddReference('PrincetonInstruments.LightField.AutomationV5')
clr.AddReference('PrincetonInstruments.LightFieldAddInSupportServices')

import PrincetonInstruments.LightField.AddIns as AddIns
from PrincetonInstruments.LightField.Automation import Automation
from PrincetonInstruments.LightField.AddIns import CameraSettings
from PrincetonInstruments.LightField.AddIns import ExperimentSettings
from PrincetonInstruments.LightField.AddIns import SpectrometerSettings
from PrincetonInstruments.LightField.AddIns import SensorTemperatureStatus

#For lightfield
def set_value(setting, value):
# Check for existence before setting
# gain, adc rate, or adc quality
    if experiment.Exists(setting):
        experiment.SetValue(setting, value)
        

def device_found():
# Find connected device
    for device in experiment.ExperimentDevices:
            if (device.Type == AddIns.DeviceType.Camera):
                return True
            # If connected device is not a camera inform the user
            print("Camera not found. Please add a camera and try again.")
            return False

# Create the LightField Application (true for visible)
# The 2nd parameter forces LF to load with no experiment
auto = Automation(True, List[String]())
                  
# Get experiment object
experiment = auto.LightFieldApplication.Experiment


#Create folder structure for data
sample = input("What sample is being scannes (e.g. C1): ") #To be included in name
date_time = f"{datetime.date.today()}-{time.localtime().tm_hour}-{time.localtime().tm_min}-{time.localtime().tm_sec}" #To be included in name
FolderName = f"C:/Users/EQUIPO/Desktop/HBN scanner/Saturation Curve/Saturation-curve-data-{sample}-{date_time}"
os.makedirs(FolderName) #Created main data folder
power_file = open(FolderName + f"/PowerData-{sample}-{date_time}.txt", 'w') # To create power file
os.makedirs(FolderName + f"/SpectrumData-{sample}-{date_time}") #Created folder for spectrum SPE files
print("New Folder Created: ", FolderName)


#Data collection loop
bins = int(input("No. of bins to sample: "))
exp_time = float(input("Exposure time (ms): "))
centre_wav = float(input("Centre wavelength (nm): "))
while True:
    take_data = input("Do you want to take another data point (y/n)? ")
    if take_data == "y":
        #Taking power
        current_power = input("Current Power (mW): ") #This will be a function from another script
        current_power = float(current_power) * 3 / 7 #To take BS into account
        print("Current power on source:", current_power, "mW")
        power_file.write(str(current_power) + "\n")
        
        #Taking spectrum
        if (device_found()==True):
            fileName = FolderName + f"/SpectrumData-{sample}-{date_time}/Spec{int(current_power*1000)}muW"
            if experiment.GetValue(CameraSettings.SensorTemperatureStatus)==SensorTemperatureStatus.Locked:
                experiment.SetLineSensorRegion(bins)
                #Set exposure timejh                                    
                set_value(CameraSettings.ShutterTimingExposureTime, exp_time)
                #set center wavelength
                set_value(SpectrometerSettings.GratingCenterWavelength , centre_wav)
                
                #Directory to save imag
                experiment.SetValue(ExperimentSettings.FileNameGenerationDirectory, Path.GetDirectoryName(fileName))
                # Set the base file name
                experiment.SetValue(
                    ExperimentSettings.FileNameGenerationBaseFileName,
                    Path.GetFileName(fileName))
        
                # Option to add date
                experiment.SetValue(
                    ExperimentSettings.FileNameGenerationAttachDate,
                    True)
        
                # Option to add time
                experiment.SetValue(
                    ExperimentSettings.FileNameGenerationAttachTime,
                    True)
                
                #Acquire data  
                try:
                    experiment.Acquire()
                    rest = exp_time//1000 + 3 
                    for i in tqdm(range(int(rest)), desc="Resting..."):
                       time.sleep(1)
                except:
                    print("Something went wrong")
            else:
                print('Temperature is not locked yet')
        else:
            print("No device found")
    elif take_data == "n":
        power_file.close()
        break
    else:
        print("Invalid input")
        