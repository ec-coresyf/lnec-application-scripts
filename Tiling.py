#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
===============================================================================
Co-ReSyF Research Application - SAR_Bathymetry
===============================================================================
 Authors: 
 Date: June/2016
 Last update: June/2017
 
 Usage: ./Tiling.py -i K5_Sesimbra_zoom.tif -o myoutput -a param.ini -v
 
 
 For help: ./Tiling.py -h
===============================================================================
"""

import os

import sys
#wdir=os.getcwd()
#paths=[wdir[:-6]+"bin"]
#for i in paths:
#    sys.path.append(i)

import numpy as np
import matplotlib.pyplot as plt
import cv2
import CSAR
import gdal
from scipy.interpolate import griddata
import matplotlib.colors as colors
from datetime import datetime
import argparse
import tarfile
import ConfigParser
import shutil


def restricted_float(x):
    x = float(x)
    if x < 0.1 or x > 0.5:
        raise argparse.ArgumentTypeError("%r not in range [0.1, 0.5]"%(x,))
    return x


########## Input arguments
parser = argparse.ArgumentParser(description='Co-ReSyF: Sar Bathymetry Research Application')
parser.add_argument('-i', '--input', help='Input image', required=True)
parser.add_argument('-b','--bath_grid', help='Bathymetric grid in a txt file',required=False)
parser.add_argument('-o', '--output', help='Output file (tar.gz) with .npz files for FFT determination', required=False)
parser.add_argument('-u', '--outlist', nargs='+', help='List with output file names (tar.gz) with .npz files for FFT determination (to be used by Wings)', required=False)
parser.add_argument('-a', '--param', help='Parameters file (.ini file)', required=True)
parser.add_argument('-p', '--polygon', help='Bathymetric AOI - Polygon coords list file', required=False)
parser.add_argument("-g", "--graphics", help="Show matplotlib plots while running the application", action="store_true")
parser.add_argument("-l", "--landmask", help="Apply Landmask",action="store_true")
parser.add_argument("-s", help="FFT box shift parameter. Possible values between (0.1-0.5). Default=0.5.",default=0.5, type=restricted_float, required=False)
parser.add_argument("-v","--verbose", help="increase output verbosity",action="store_true")

args = parser.parse_args()

RunId = datetime.now().strftime('%Y%m%dT%H%M%S')

# Creating ini file with parameters    
parOut = open(args.param, "w")
Config = ConfigParser.ConfigParser()
 
Config.add_section("Arguments")
Config.set("Arguments", "Input_file", args.input)
Config.set("Arguments", "Output_file", args.output)
Config.set("Arguments", "Polygon_file", args.polygon)
Config.set("Arguments", "Graphics", args.graphics)
Config.set("Arguments", "Landmask", args.landmask)
Config.set("Arguments", "FFT_box_shift", args.s)
Config.set("Arguments", "Verbose", args.verbose)
Config.add_section("Run")
Config.set("Run", "Id", RunId)

Config.write(parOut)
parOut.close()

# Creating parameters
Input = args.input
Output = args.output
Polygon = args.polygon
Graphics = args.graphics
Landmask = args.landmask
shift = args.s
Verbose = args.verbose

# Creating temp folder (for temporary files)
curdir = os.getcwd()
Path_temp = curdir + '/temp/' 
PathOut = Path_temp + str(RunId) + "/FFT_img_outputs"
if not os.path.exists(PathOut):
    os.makedirs(PathOut)


#### Hardcoded flags...
SFactor=1./1.
Slant_Flag=False
EPSG="WGS84"
#######################

#################################################################
#################################################################
#################################################################
#################################################################
print "\n------- Starting Tiling -------"

if args.verbose:
    print "\n\nReading Image..."
img, mask, res, LMaskFile = CSAR.ReadSARImg(args.input, ScaleFactor=np.float(SFactor),
                                            C_Stretch=True, SlantCorr=Slant_Flag, EPSG_flag=EPSG,
                                            Land=Landmask, path=PathOut)

if args.verbose:
    print "\n\nReading Image... DONE!!!"

lon, lat = CSAR.GetLonLat(LMaskFile)


# Saving list with variable 'res' into parameter file
cfgfile = open(args.param, 'w')
Config.set("Run", "res", str(res[0]) + ', ' + str(res[1]) ) 
Config.write(cfgfile)
cfgfile.close


### Offset = # of pixels for half of 1 km FFT box. 
### Therefore, the Offset varies with image resolution. 
offset=CSAR.GetBoxDim(res[0])
if args.verbose:
    print "\nOffset (pixels,m):  (  %s  ;  %s  ) " % (offset,offset*res[0]) +"\n"

############################################################
###### Grid definition
############################################################
############################################################

##########################################################
# RCCC AND RIAA NEW CODE ################################
##########################################################
# Load the grid from txt file and convert to list
corrected_grid = np.loadtxt(args.bath_grid)
corrected_grid = corrected_grid.tolist()

#Find the nearest pixels in the image that correspond to the grid points
LonVec, LatVec = lon[0,:], lat[:,0]
Pontos=[]
for i in corrected_grid:
    valx, lon_index = CSAR.find_nearest(LonVec,i[0])
    valy, lat_index = CSAR.find_nearest(LatVec,i[1])
    Pontos.append([lon_index,lat_index])
Pontos = np.array(Pontos)

if Graphics == 'True': #Graphics
    plt.figure()
    plt.imshow(img,cmap="gray")
    plt.scatter(Pontos[:,0],Pontos[:,1],3,marker='o',color='r')
    plt.savefig(PathOut+"Grid.png", dpi=300)
    plt.show()


############################################################
############################################################
####   Preparing files for FFT determination and plot  #####
############################################################
if args.verbose:
        print "Creating the FFT image subsets for each grid point... "


for n,i in enumerate(Pontos):
    Point_id=str(n+1)
    
    if args.output:
        npz_tar_file = args.output + str(RunId) + "_FFT_" + Point_id + ".tar.gz"
    else:
        npz_tar_file = args.outlist[n]

    tar = tarfile.open(npz_tar_file, "w")
    imgs,lons,lats=CSAR.GetFFTBoxes(i,img,lon,lat,offset,shift)
    for m,j in enumerate(imgs):
        FFTid = str(n+1)+"."+str(m+1)
        npzOut = npz_tar_file[:-7] + "_" + FFTid + ".npz"
        np.savez(npzOut, lons=lons[m], lats=lats[m], imgs=imgs[m])
        tar.add( npzOut, os.path.basename(npzOut) )
        os.remove (npzOut)
    tar.close()
if args.verbose:
        print "The FFT .npz files were successfully created !!! "


# Removing temporary folder
shutil.rmtree(Path_temp)