#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
===============================================================================
Co-ReSyF Research Application - SAR_Bathymetry
===============================================================================
 Authors: Alberto Azevedo and Francisco Sancho
 Date: June/2016
 Last update: March/2017
 
 Usage: ./SAR_Bathymetry_CoReSyF_V8.py <image input file> 
 
 For help: ./SAR_Bathymetry_CoReSyF_V8.py -h
===============================================================================
"""

import os,sys
wdir=os.getcwd()
paths=[wdir[:-6]+"bin"]
for i in paths:
	sys.path.append(i)

import numpy as np
import matplotlib.pyplot as plt
import cv2
import CSAR
import gdal
from scipy.interpolate import griddata
import matplotlib.colors as colors
from datetime import datetime
import argparse
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
parser.add_argument('-o', '--output', help='Output image name', required=True)
parser.add_argument('-a', '--out_param', help='Output parameters file (.ini file)', required=True)
parser.add_argument('-p', '--polygon', help='Bathymetric AOI - Polygon coords list file', required=False)
parser.add_argument("-g", "--graphics", help="Show matplotlib plots while running the application", action="store_true")
parser.add_argument("-l", "--landmask", help="Apply Landmask",action="store_true")
parser.add_argument("-r", "--resDx", help="Resolution of the final bathymetric grid, in meters (m). Default=500m.", default=500., type=float, required=False)
parser.add_argument("-s", help="FFT box shift parameter. Possible values between (0.1-0.5). Default=0.5.",default=0.5, type=restricted_float, required=False)
parser.add_argument("-v","--verbose", help="increase output verbosity",action="store_true")
args = parser.parse_args()
 
filein=args.input
fileout = args.output
Graphics=args.graphics
GridDx=args.resDx
#Tmax=args.t
shift=args.s
RunId=datetime.now().strftime('%Y%m%dT%H%M%S')
#RunId=datetime.now().strftime('%Y%m%dT%H%M')
#PathOut = os.path.dirname(os.path.realpath(filein))
#PathOut="../output/SAR_BathyOut_"+str(RunId)+"/"
#newpath = r'./'+PathOut
#if not os.path.exists(newpath):
#	os.makedirs(newpath)


#Creating Temporary folder
curdir = os.getcwd()
Path_temp = curdir + '/temp/' 
if not os.path.exists(Path_temp):
	os.makedirs(Path_temp)

# Creating ini file with parameters    
parOut = open(args.out_param, "w")
Config = ConfigParser.ConfigParser()
 
Config.add_section("Arguments")
Config.set("Arguments", "Input_file", args.input)
Config.set("Arguments", "Output_file", args.output)
Config.set("Arguments", "Polygon_file", args.polygon)
Config.set("Arguments", "Graphics", args.graphics)
Config.set("Arguments", "Grid_resolution", args.resDx)
Config.set("Arguments", "FFT_box_shift", args.s)
Config.set("Arguments", "Landmask", args.landmask)
Config.set("Arguments", "Verbose", args.verbose)
Config.add_section("Run")
Config.set("Run", "Id", RunId)

Config.write(parOut)
parOut.close()


#### Hardcoded flags...
SFactor=1./1.
Slant_Flag=False
EPSG="WGS84"
#######################


#################################################################
#################################################################
### TO DO - Read EMODNET to define Tmax

#Tmax=12.## Swell com periodo de 15 segundos
#Lmax=(9.8*(Tmax*Tmax))/(2*np.pi)
#W2_deep=(2.*np.pi/(Tmax))*(2.*np.pi/(Tmax))
#print "LMAX" , Lmax
#################################################################
#################################################################
#################################################################
#################################################################


if args.verbose:
	print "\n\nReading Image..."
img,mask,res, LMaskFile=CSAR.ReadSARImg(filein,ScaleFactor=np.float(SFactor),C_Stretch=True,SlantCorr=Slant_Flag,EPSG_flag=EPSG,Land=args.landmask, path=Path_temp)

if args.verbose:
	print "\n\nReading Image... DONE!!!"

lon,lat=CSAR.GetLonLat(LMaskFile)

###
### Offset = # of pixels for half of 1 km FFT box. 
### Therefore, the Offset varies with image resolution. 
offset=CSAR.GetBoxDim(res[0])
if args.verbose:
	print "\nOffset (pixels,m):  (  %s  ;  %s  ) " % (offset,offset*res[0]) +"\n"

############################################################
###### Grid definition 
############################################################
############################################################
Pts=CSAR.SetGrid(LMaskFile,res,GridDeltaX = GridDx)
LonVec,LatVec=lon[0,:],lat[:,0]
Pontos=[]
for i in Pts:
	valx, lon_index=CSAR.find_nearest(LonVec,i[0])
	valy, lat_index=CSAR.find_nearest(LatVec,i[1])
	Pontos.append([lon_index,lat_index])
Pontos = np.array(Pontos)

if args.polygon==None:
	Polygon=CSAR.SetPolygon(LMaskFile,offset,PtsNum=10)
	np.savetxt("Polygon.txt",Polygon)
	os.system("cp -f Polygon.txt "+Path_temp+".")
	for i in Polygon:
		print i
else:
	os.system("cp -f "+args.polygon+" "+Path_temp+".")
	Polygon=np.loadtxt(args.polygon)
	print Polygon	

cnt=Polygon.reshape((-1,1,2)).astype(np.float32)

Pts2Keep=[]
for m,k in enumerate(Pts):
	Result=cv2.pointPolygonTest(cnt, (k[0],k[1]), False)
	if Result!=-1.0:
		Pts2Keep.append(m)
Pontos=Pontos[Pts2Keep]
#print Pontos_Final.shape


plt.figure()
plt.imshow(img,cmap="gray")
plt.scatter(Pontos[:,0],Pontos[:,1],3,marker='o',color='r')
plt.savefig(Path_temp+"Grid.png", dpi=300)
if Graphics:
	plt.show()

if args.verbose:
	print "\n\n"
	print Pontos.shape
	print "\n\n"

#Move the input image to the output filepath
os.rename(filein, fileout)


filename, file_extension = os.path.splitext(fileout)

metadata_filepath=filename+'.met'
print metadata_filepath
metadata_file=open(metadata_filepath,"w")
metadata_file.write("NumberTiles = %s" % Pontos.shape[0])
metadata_file.close()

# Removing temporary folder
shutil.rmtree(Path_temp)