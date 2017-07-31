#!/usr/bin/python2.7
# -*- coding: utf-8 -*-


"""
===============================================================================
REMOTE SENSING FUNCTIONS USED IN SAR_Bathymetry_CoReSyF_V8.py
developed in: OPENCV (cv2), PIL, skimage, matplotlib, numpy, GDAL, etc.

===============================================================================
 Authors: Alberto Azevedo and Francisco Sancho
 Date: June/2016
 Last update: March/2017
 ===============================================================================
"""
import time
import os
import sys
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import cv2
#import PIL.Image as Image
from skimage import exposure
from osgeo import gdal, osr
from pyproj import Proj, transform
import netCDF4 as ncdf
from scipy import ndimage
import glob
from scipy.interpolate import griddata
import matplotlib.colors as colors
import math


def find_nearest(array, value):
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx


def text_labels(array_in=np.array([]), form='10.2e'):
    list_out = []
    for i in array_in:
        list_out.append(str(format(i, form)))
    return list_out


def rads2deg(radians):
    return radians * (180 / np.pi)


def scale_img(img, type):
    """
    If type = 8 => dtype=np.uint8 => n_colors = 256 and range from 0 to 255
    If type = 16 => dtype=np.uint16 => n_colors = 65536 and range from 0 to 65535
    If type = 32 => dtype=np.float32 => n_colors = 1 and range from 0 to 1.
    """
    n_colors = {"8": 255., "16": 65536., "32": 1.}
    if type == 8:
        out_type = np.uint8
    elif type == 16:
        out_type = np.uint16
    elif type == 32:
        out_type = np.float32
    else:
        print "ERROR! Check <type> argument!!!"
    img_new = np.array(
        img * n_colors[str(type)] / np.nanmax(img), dtype=out_type)
    return img_new


# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []
cropping = False
drawing = False  # true if mouse is pressed
ix, iy = -1, -1


def cvPlot(img, Title='img', width=800, cmap=cv2.COLORMAP_BONE):
    # Resize Window
    r = float(width) / img.shape[1]
    dim = (width, int(img.shape[0] * r))
    # perform the actual resizing of the image and show it
    img = cv2.resize(img, dim, interpolation=cv2.INTER_NEAREST)
    # false=cv2.applyColorMap(img,cmap)
    # Plot image
#	cv2.imshow(Title,false)
    cv2.imshow(Title, img)
    k = cv2.waitKey()
    if k == 27:  # k = 27 => Key 'Esc'
        cv2.destroyWindow(Title)
    return None


def ContrastStretch(img, limits=(1, 99)):
    res = scale_img(img, 32)
    # Contrast stretching with skimage (http://scikit-image.org/docs/dev/auto_examples/plot_equalize.html)
    p_bottom, p_top = np.percentile(res, limits)
    img_rescale = exposure.rescale_intensity(res, in_range=(p_bottom, p_top))
    img_new = scale_img(img_rescale, 16)
    return img_rescale


def ContrastStretch2(img, limits=(0, 3)):
    img = scale_img(img, 32)
    p_bottom, p_top = np.percentile(img, limits)
    img_new = ((img - img.min()) * ((p_top - p_bottom) /
                                    (img.max() - img.min()))) + p_bottom
    img_new = scale_img(img_new, 16)
    return img_new


def array2raster(img, lon, lat, EPSG_out=4326, fileout="ImgOut.tif"):
    import numpy as np
    from osgeo import gdal
    from osgeo import gdal_array
    from osgeo import osr
    import matplotlib.pylab as plt
    import cv2

    # For each pixel I know it's latitude and longitude.
    # As you'll see below you only really need the coordinates of
    # one corner, and the resolution of the file.

    img = scale_img(img, 8)

    xmin, ymin, xmax, ymax = [lon.min(), lat.min(), lon.max(), lat.max()]
    # print xmin,ymin,xmax,ymax

    if len(img.shape) > 2:
        nrows, ncols = np.shape(img[0, :, :])
    else:
        nrows, ncols = np.shape(img)
    xres = (xmax - xmin) / float(ncols)
    yres = (ymax - ymin) / float(nrows)
    geotransform = (xmin, xres, 0, ymax, 0, -yres)
    # That's (top left x, w-e pixel resolution, rotation (0 if North is up),
    #         top left y, rotation (0 if North is up), n-s pixel resolution)
    # I don't know why rotation is in twice???

    output_raster = gdal.GetDriverByName('GTiff').Create(
        fileout, ncols, nrows, 1, gdal.GDT_Byte)  # Open the file
    output_raster.SetGeoTransform(geotransform)  # Specify its coordinates
    srs = osr.SpatialReference()                 # Establish its coordinate encoding
    # This one specifies WGS84 lat long.
    srs.ImportFromEPSG(EPSG_out)
    # Exports the coordinate system
    output_raster.SetProjection(srs.ExportToWkt())
    # to the file

    output_raster.GetRasterBand(1).WriteArray(
        img)   # Writes my array to the raster
    output_raster.GetRasterBand(1).SetNoDataValue(0)
    return None


def SetPolygon(filein, offset, fileout="ImgProfile.tif", PtsNum=10):

    def Set_Profile(event, x, y, flags, param):
        # if the left mouse button was clicked, record the
        # (x, y) coordinates
        if event == cv2.EVENT_LBUTTONDOWN:
            refPt.append((x, y))
            cv2.circle(image, (x, y), 2, (0, 0, 255), 3)

    # load the image, clone it, and setup the mouse callback function
    image = cv2.imread(filein, 1)
    lon1, lat1 = GetLonLat(filein)
    box = np.zeros((offset * 2, offset * 2))

    # Resize Window
    width = 1200
    r = float(width) / image.shape[1]
    dim = (width, int(image.shape[0] * r))
    # perform the actual resizing of the image and show it
    image = cv2.resize(image, dim, interpolation=cv2.INTER_NEAREST)
    lon1 = cv2.resize(lon1, dim, interpolation=cv2.INTER_NEAREST)
    lat1 = cv2.resize(lat1, dim, interpolation=cv2.INTER_NEAREST)

    dim2 = (int(box.shape[1] * r), int(box.shape[0] * r))
    box1 = cv2.resize(box, dim2, interpolation=cv2.INTER_NEAREST)
    offBox = box1.shape[0]

    clone = image.copy()
    lon2 = lon1.copy()
    lat2 = lat1.copy()

    cv2.namedWindow("image")
    cv2.setMouseCallback("image", Set_Profile)

    refPt = []
    CoordsPtsAux = np.zeros((50, 2))
    CoordsPts = []
    print """
####################################
#   Press 'r' to reset points.     #
#   Press 's' to save points.      #
#   Press 'q' to quit.             #
####################################
"""
    # keep looping until the 'q' key is pressed
    while True:
        # display the image and wait for a keypress
        cv2.imshow("image", image)
        key = cv2.waitKey(1) & 0xFF

        # if the 'r' key is pressed, reset the points
        if key == ord("r"):
            refPt = []
            image = clone.copy()
        # if the 's' key is pressed, save the points
        elif key == ord("s"):
            # -- Extract the line...
            # Make a line with "num" points...
            Pt = np.array(refPt)
            # for lista in Pt:
            # 	print lista
            xLine, yLine = Pt[:, 0], Pt[:, 1]
            LonVec = lon1[0, :]
            LatVec = lat1[:, 0]

            print "\n"
            for n in xrange(Pt.shape[0]):
                xaux, yaux = Pt[n, 0], Pt[n, 1]
                CoordsPtsAux[n, 0], CoordsPtsAux[n, 1] = LonVec[np.int(
                    round(xaux))], LatVec[np.int(round(yaux))]
                CoordsPts.append([CoordsPtsAux[n, 0], CoordsPtsAux[n, 1]])
                print "P" + str(n) + ": (", xaux, ",", yaux, ")  ==>> (", CoordsPtsAux[n, 0], ",", CoordsPtsAux[n, 1], ")"
            CoordsPts = np.array(CoordsPts)
            Pt = Pt.reshape((-1, 1, 2))
            cv2.polylines(image, [Pt], True, (0, 255, 0), 3)
            for i in xrange(Pt.shape[0]):
                cv2.circle(image, (np.int(round(xLine[i])), np.int(
                    round(yLine[i]))), 2, (0, 0, 255), 2)
        # if the 'q' key is pressed, break from the loop
        elif key == ord("q"):
            cv2.destroyWindow("image")
            break
    return CoordsPts


def SetGrid(filein, res, GridDeltaX=500.):
    image = cv2.imread(filein, 1)
    lon1, lat1 = GetLonLat(filein)

    gridRes = GridDeltaX / res[0]
    pLon = lon1[::np.int(gridRes), ::np.int(gridRes)].flatten()
    pLat = lat1[::np.int(gridRes), ::np.int(gridRes)].flatten()
    points = []
    for n, i in enumerate(pLon):
        points.append([pLon[n], pLat[n]])
    CoordsPts = np.array(points)
    return CoordsPts


def SlantRangeCorrection(img):
    #img=np.where(img<0, np.nan, img)
    #plt.imshow(img,cmap=plt.cm.gray), plt.show(), sys.exit()
    slant_profile = np.mean(img, axis=0)
    #plt.plot(slant_profile), plt.show(), sys.exit()
    width = img.shape[1]
    window = int(width * 0.15)
    s_min, smax = np.nanmean(slant_profile[:window]), np.nanmean(
        slant_profile[-window:])
    slant_corr = np.linspace(s_min, smax, num=slant_profile.shape[0])
    #plt.plot(slant_corr), plt.show(), sys.exit()
    slant_corr = slant_corr[::-1]
    img_corr = img * slant_corr[:, np.newaxis].transpose()

    #plt.figure(), plt.imshow(img,cmap=plt.cm.gray)
    #plt.figure(), plt.imshow(img_corr,cmap=plt.cm.gray)
    #plt.show(), sys.exit()
    return img_corr


def GetLonLat(filein):
    ImgSize = GetImgSize(filein)
    Coords = GetCoords(filein)
    lon = np.zeros(ImgSize, dtype=np.float32)
    lat = np.zeros_like(lon)
    Lat_vals = np.linspace(Coords[:, 1].min(), Coords[:, 1].max(), ImgSize[0])
    for i in xrange(ImgSize[0]):
        lon[i] = np.linspace(Coords[:, 0].min(),
                             Coords[:, 0].max(), ImgSize[1])
        lat[i] = np.ones((ImgSize[1])) * Lat_vals[i]
    lat = lat[::-1, :]
    return lon, lat


def SlantRange(filein):
    f = gdal.Open(filein)
    a = f.GetRasterBand(1)
    img = f.ReadAsArray(0, 0, a.XSize, a.YSize).astype(np.uint16)
    img1 = ContrastStretch(img)
    img2 = SlantRangeCorrection(img1)
    lon, lat = GetLonLat(filein)
    fileout = filein[:-4] + "_Slant.tif"
    array2raster(img2, lon, lat, fileout=fileout)
    print "Slant-Range Correction Done!!!"
    return fileout


def LandMask(filein_ROI, dim, fileout="LandMask.tif", Pname="../output/SAR_BathyOut/"):
    """
    # http://www.viewfinderpanoramas.org/Coverage%20map%20viewfinderpanoramas_org3.htm
    # 
    # In order to impose a Global LandMask, the file Topography.tif must have the global topography.
    # Presently Topography.tif only represents Iberian Peninsula 
    #
    """
    ImgSize = GetImgSize(filein_ROI)
    Coords = GetCoords(filein_ROI)
    ImgRes = GetImgRes(filein_ROI, dim, path=Pname)

    TopoFile = "../input/VFP/Topography.tif"
    f = gdal.Open(TopoFile)
    a = f.GetRasterBand(1)
    Topo = f.ReadAsArray()
    Topo = np.where(Topo == np.nan, 0., Topo)

    Tlon, Tlat = GetLonLat(TopoFile)

    with np.errstate(invalid='ignore'):
        Topo = np.where(Topo > 0., 0., 255.)

    if Coords[:, 0].min() > 180.:
        xmin, xmax, ymin, ymax = Coords[:, 0].min(
        ) - 360., Coords[:, 0].max() - 360., Coords[:, 1].min(), Coords[:, 1].max()
        coords_flag = True
    else:
        xmin, xmax, ymin, ymax = Coords[:, 0].min(), Coords[:, 0].max(
        ), Coords[:, 1].min(), Coords[:, 1].max()
        coords_flag = False
    # print "\n\nCoords da Imagem: ",xmin,xmax,ymin,ymax,coords_flag,"\n\n"

    res_lon = Tlon[0, 1] - Tlon[0, 0]
    res_lat = Tlat[0, 0] - Tlat[1, 0]

    Lon_min = np.where(Tlon[0, :] >= xmin)
    Lon_max = np.where(Tlon[0, :] <= xmax)
    # print Lon_min, Lon_max, xmin, xmax,Tlon[0,:]

    iLon1, iLon2 = Lon_min[0][0], Lon_max[0][-1]

    Lat_min = np.where(Tlat[:, 0] >= ymin)
    Lat_max = np.where(Tlat[:, 0] <= ymax)
    iLat1, iLat2 = Lat_max[0][0], Lat_min[0][-1]

    Tlon = Tlon[iLat1:iLat2, iLon1:iLon2]
    if coords_flag == True:
        Tlon = np.where(Tlon <= 0., 360. + Tlon, Tlon)
    Tlat = Tlat[iLat1:iLat2, iLon1:iLon2]
    Topo = Topo[iLat1:iLat2, iLon1:iLon2]

    # plt.subplot(111),plt.imshow(Topo,cmap=plt.cm.jet),plt.show()

    array2raster(Topo, Tlon, Tlat, EPSG_out=4326,
                 fileout=Pname + "AA_TOPO_VFP.tif")

    mask1 = cv2.imread(filein_ROI, -1)
    Tlon1, Tlat1 = GetLonLat(filein_ROI)

    Topo = cv2.imread(Pname + "AA_TOPO_VFP.tif", -1)
    ret, th1 = cv2.threshold(mask1, 127, 255, cv2.THRESH_BINARY_INV)
    ret, th2 = cv2.threshold(Topo, 127, 255, cv2.THRESH_BINARY_INV)

    kernel = np.ones((5, 5), np.uint8)
    th1 = cv2.dilate(th1, kernel, iterations=2)
    array2raster(th1, Tlon1, Tlat1, EPSG_out=4326, fileout=filein_ROI)
    array2raster(th2, Tlon, Tlat, EPSG_out=4326,
                 fileout=Pname + "AA_TOPO_VFP.tif")

    # plt.figure()
    # plt.subplot(121),plt.imshow(th1,cmap=plt.cm.gray)
    # plt.subplot(122),plt.imshow(th2,cmap=plt.cm.gray)
    # plt.show()

    cmd1 = "rm -f " + fileout

    cmd2 = "gdal_merge.py -n 0. -o " + fileout + " " + \
        filein_ROI + " " + Pname + "AA_TOPO_VFP.tif"
    # print cmd1
    os.system(cmd1)
    # print cmd2
    os.system(cmd2)

    LandMask = cv2.imread(fileout, -1)
    ret, LandMask_inv = cv2.threshold(
        LandMask, 127, 255, cv2.THRESH_BINARY_INV)

#	plt.figure()
#	plt.subplot(131),plt.imshow(mask1,cmap=plt.cm.gray)
#	plt.subplot(132),plt.imshow(LandMask,cmap=plt.cm.gray)
#	plt.subplot(133),plt.imshow(LandMask_inv,cmap=plt.cm.gray)
#	plt.show()

    MaskFinal = scale_img(LandMask_inv, 8)
    lon, lat = GetLonLat(filein_ROI)
    array2raster(MaskFinal, lon, lat, EPSG_out=4326, fileout=fileout)
    print "Landmask Done!!!"
    return MaskFinal


def GetImgSize(filein):
    os.system("gdalinfo " + filein + " > Info_ImgSize.txt")
    fid = open("Info_ImgSize.txt", "r")
    data = fid.readlines()
    for n, line in enumerate(data):
        if re.search("Size is ", line):
            LineSize = n
    y = np.int(data[LineSize].split(" is ")[1].split(",")[1])
    x = np.int(data[LineSize].split(" is ")[1].split(",")[0])
    ImgSize = [y, x]
    fid.close()
    os.system("rm -f Info_ImgSize.txt")
    return ImgSize


def GetCoords(filein):
    os.system("gdalinfo " + filein + " > Info_Coords.txt")
    fid = open("Info_Coords.txt", "r")
    data = fid.readlines()
    for n, line in enumerate(data):
        if re.match("Corner Coordinates:", line):
            LineCoords = n
    Coords = [[np.float(data[LineCoords + 1].split("(")[1].split(",")[0]), np.float(data[LineCoords + 1].split("(")[1].split(",")[1].split(")")[0])],
              [np.float(data[LineCoords + 2].split("(")[1].split(",")[0]),
               np.float(data[LineCoords + 2].split("(")[1].split(",")[1].split(")")[0])],
              [np.float(data[LineCoords + 3].split("(")[1].split(",")[0]),
               np.float(data[LineCoords + 3].split("(")[1].split(",")[1].split(")")[0])],
              [np.float(data[LineCoords + 4].split("(")[1].split(",")[0]), np.float(data[LineCoords + 4].split("(")[1].split(",")[1].split(")")[0])]]
    fid.close()
    os.system("rm -f Info_Coords.txt")
    Coords = np.array(Coords)
    return Coords


def GetImgRes(filein, dim, path="../output/SAR_BathyOut/"):

    from osgeo import gdal, osr
    import glob

    files = glob.glob(path + "*ETRS89.tif")
    if len(files) != 0:
        fout = files[0]
    else:
        fout = path + filein[:-4].split("/")[-1] + "_ETRS89.tif"

    if not os.path.isfile(fout):
        print "\nETRS89 file doesn't exists...\n"
        print "\nCalculating the resolution of the image..."
        print filein

        f = gdal.Open(filein)

        sourceSR = osr.SpatialReference()
        try:
            sourceSR.ImportFromWkt(f.GetProjectionRef())
        except:
            sourceSR.ImportFromWkt(f.GetGCPProjection())
        ProjLines = sourceSR.ExportToPrettyWkt()

        EPSG_source = ProjLines.split(
            "AUTHORITY")[-1].split(",")[1].split("\"")[1]
        # print EPSG_source, filein, fout
        if (dim[0] == 0. and dim[1] == 0.):
            os.system("gdalwarp -overwrite -srcnodata 0 -dstnodata 0 -s_srs EPSG:" +
                      EPSG_source + " -t_srs EPSG:3763 " + filein + " " + fout)
        else:
            os.system("gdalwarp -overwrite -srcnodata 0 -dstnodata 0 -r average -ts " + str(dim[0]) + " " + str(
                dim[1]) + " -s_srs EPSG:" + EPSG_source + " -t_srs EPSG:3763 " + filein + " " + fout)
    else:
        print "\nETRS89 file already exists..."
        print "Determining image resolution..."

    os.system("gdalinfo " + fout + " > Info_Coords.txt")
    fid = open("Info_Coords.txt", "r")
    data = fid.readlines()
    for n, line in enumerate(data):
        if re.match("Pixel Size", line):
            LineRec = n
    line = data[LineRec]
    xres = round(np.float(line.split(",")[0].split("(")[1]), 2)
    yres = round(np.abs(np.float(line.split(",")[1].split(")")[0])), 2)
    ImgRes = [yres, xres]
    fid.close()
    os.system("rm -f Info_Coords.txt")
    print "Image Resolution (Lat/Lon): ", ImgRes
    return ImgRes


def GetImgType(filein):
    os.system("gdalinfo " + filein + " > Info_Type.txt")
    fid = open("Info_Type.txt", "r")
    data = fid.readlines()
    for n, line in enumerate(data):
        if re.search("Driver:", line):
            type = line.split(":")[1].strip()
    ImgType = {"ERS1/2": False, "ENVISAT": False,
               "TSX": False, "GeoTIFF": False}
    if type == "ESAT/Envisat Image Format":
        ImgType["ENVISAT"] = True
    elif type == "SAR_CEOS/CEOS SAR Image":
        ImgType["ERS1/2"] = True
    elif type == "TSX/TerraSAR-X Product":
        ImgType["TSX"] = True
    elif type == "SAFE/Sentinel-1 SAR SAFE Product":
        ImgType["Sentinel1"] = True
    elif type == "GTiff/GeoTIFF":
        ImgType["GeoTIFF"] = True
    else:
        print "Unknown Driver..."
        pass
    fid.close()
    os.system("rm -f Info_Type.txt")
    return ImgType


def SlantRangeGTiFF(filein, fileout, EPSG=4326):
    f = gdal.Open(filein)
    a = f.GetRasterBand(1)
    img = f.ReadAsArray(0, 0, a.XSize, a.YSize).astype(np.uint16)
    Metadata = f.GetMetadata()
    ncols, nrows = a.XSize, a.YSize

    GCPs = f.GetGCPs()
    geotransform = f.GetGeoTransform()

    img1 = ContrastStretch(img)
    img2 = SlantRangeCorrection(img1)
    img3 = scale_img(img2, 8)

    output_raster = gdal.GetDriverByName('GTiff').Create(
        fileout, ncols, nrows, 1, gdal.GDT_Byte)  # Open the file
    output_raster.SetGeoTransform(geotransform)  # Specify its coordinates
    srs = osr.SpatialReference()                 # Establish its coordinate encoding
    # This one specifies WGS84 lat long.
    srs.ImportFromEPSG(EPSG)
    # Exports the coordinate system
    output_raster.SetProjection(srs.ExportToWkt())
    # to the file
    output_raster.SetGCPs(GCPs, f.GetGCPProjection())
    output_raster.SetMetadata(Metadata)
    output_raster.GetRasterBand(1).WriteArray(
        img3)   # Writes my array to the raster
    output_raster.GetRasterBand(1).SetNoDataValue(0)
    output_raster = None
    return None


def sigma0(img):
    imgOut = 10. * np.log10(img)  # sigma0
    return imgOut


def ReadSARImg(filein, ScaleFactor=1., C_Stretch=False, SlantCorr=True, EPSG_flag="WGS84", Land=False, path="../output/SAR_BathyOut/", band=1):

    ImgType = GetImgType(filein)

    if SlantCorr:
        if (ImgType["ENVISAT"] or ImgType["ERS1/2"]):
            fileout_slant = path + filein[:-4] + "_Slant.tif"
            SlantRangeGTiFF(filein, fileout_slant)
            filein = fileout_slant

    ImgSize = GetImgSize(filein)

    if EPSG_flag == "WGS84":
        EPSG = "4326"
    elif EPSG_flag == "ETRS89":
        EPSG = "3763"
    else:
        pass

    file_aux1 = path + filein[:-4].split("/")[-1] + "_scaled.tif"

    if ScaleFactor != 1:
        dim = (int(ImgSize[1] * ScaleFactor), int(ImgSize[0] * ScaleFactor))
        if not os.path.isfile(file_aux1):
            print "\nCreating an " + EPSG_flag + " image file..."
            os.system("gdalwarp -overwrite -srcnodata 0 -dstnodata 0 -r average -ts " + str(
                dim[0]) + " " + str(dim[1]) + " -t_srs EPSG:" + EPSG + " " + filein + " " + file_aux1)
        else:
            print file_aux1, " Already Exists..."
    else:
        dim = [0, 0]
        if not os.path.isfile(file_aux1):
            os.system("gdalwarp -overwrite -srcnodata 0 -dstnodata 0 -r average -t_srs EPSG:" +
                      EPSG + " " + filein + " " + file_aux1)
        else:
            print file_aux1, " Already Exists..."

    lon, lat = GetLonLat(file_aux1)
    res = GetImgRes(filein, dim, path=path)

    f = gdal.Open(file_aux1)
    a = f.GetRasterBand(1)
    img = f.ReadAsArray(0, 0, a.XSize, a.YSize).astype(np.uint16)

    ### Sigma0 ###########
    # img=sigma0(img.clip(min=0.00000001))

    BandMask = a.GetMaskBand()
    mask = BandMask.ReadAsArray()

    fileCS = glob.glob(path + "*_CS.tif")

    if C_Stretch:
        if len(fileCS) == 0:
            print "\nContrast-Stretch..."
            ti = time.clock()
            img = ContrastStretch(img)
            if len(img.shape) == 3:
                img = img[band - 1, :, :]

            array2raster(img, lon, lat, fileout=path +
                         filein[:-4].split("/")[-1] + "_CS.tif")
            tf = time.clock()
            print tf - ti, "  =>  Performing ContrastStretch"
        else:
            f = gdal.Open(fileCS[0])
            a = f.GetRasterBand(1)
            img = f.ReadAsArray(0, 0, a.XSize, a.YSize).astype(np.uint16)
            if len(img.shape) == 3:
                img = img[band - 1, :, :]

    else:
        os.system("cp " + file_aux1 + " " + path +
                  filein[:-4].split("/")[-1] + "_CS.tif")

    fmask = path + filein[:-4].split("/")[-1] + "_Mask.tif"

    array2raster(mask, lon, lat, fileout=fmask)

    LMaskFile = path + filein[:-4].split("/")[-1] + "_CS.tif"
    if Land == True:
        MaskFinal = LandMask(fmask, dim, fileout=path +
                             filein[:-4].split("/")[-1] + "_MaskFinal.tif", Pname=path)
        img = cv2.bitwise_and(img, img, mask=MaskFinal)
        array2raster(img, lon, lat, EPSG_out=4326, fileout=path +
                     filein[:-4].split("/")[-1] + "_Masked.tif")
        mask = MaskFinal
        LMaskFile = path + filein[:-4].split("/")[-1] + "_Masked.tif"

    return img, mask, res, LMaskFile


def sector_mask(shape, centre, radius, angle_range):
    """
    Return a boolean mask for a circular sector. The start/stop angles in
    `angle_range` should be given in clockwise order.
    """

    x, y = np.ogrid[:shape[0], :shape[1]]
    cx, cy = centre
    tmin, tmax = np.deg2rad(angle_range)

    # ensure stop angle > start angle
    if tmax < tmin:
        tmax += 2 * np.pi

    # convert cartesian --> polar coordinates
    r2 = (x - cx) * (x - cx) + (y - cy) * (y - cy)
    theta = np.arctan2(x - cx, y - cy) - tmin

    # wrap angles between 0 and 2*pi
    theta %= (2 * np.pi)

    # circular mask
    circmask = r2 <= radius * radius

    # angular mask
    anglemask = theta <= (tmax - tmin)

    return circmask * anglemask


""" How to use the sector_mask function...
http://stackoverflow.com/questions/18352973/mask-a-circular-sector-in-a-numpy-array

from matplotlib import pyplot as pp
from scipy.misc import lena

matrix = lena()
mask = sector_mask(matrix.shape,(200,100),300,(0,50))
matrix[~mask] = 0
pp.imshow(matrix)
pp.show()
"""


def groupedAvg(myArray, N=6):
    result = np.nancumsum(myArray, 0)[N - 1::N] / float(N)
    result[1:] = result[1:] - result[:-1]
    return result


def checkRacio(CDO, Tmax):
    Lmax = (9.8 * (Tmax * Tmax)) / (2 * np.pi)
    racio = CDO / Lmax
    RacioThreshold = 0.996
    if (racio >= RacioThreshold):
        CDO = np.nan
    return CDO


#################################################################
#################################################################
#############          Depth inversion        ###################
#################################################################
#################################################################
def SAR_LinearDepth(CDO, W2, Lmax):
    # W2_deep=(2.*np.pi/Tmax)*(2.*np.pi/Tmax)
    if CDO == np.nan:
        depth = 200.
    else:
        depth = (CDO / (2. * np.pi)) * \
            np.arctanh((W2 * CDO) / (2. * np.pi * 9.8))

    return depth
#################################################################


#################################################################
#################################################################
###############       FFT Box calculation     ###################
#################################################################
#################################################################
def FFT_SAR(img, lon, lat, fout, FFT_id, Lmax, res=1.25, Tmax=12., verbose=False):
    """
    inputs: img
            point = (x,y) center of the FFT box
            box_dim = dimensions of the FFT box
            res= image resolution in meters (meters per pixel)
    outputs:
            CDO and Direction
    """
    center = [lon[lon.shape[0] / 2, lon.shape[1] / 2],
              lat[lat.shape[0] / 2, lat.shape[1] / 2]]

    # FFT determination
    dft = cv2.dft(np.float32(img), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    magnitude, phase = cv2.cartToPolar(dft_shift[:, :, 0], dft_shift[:, :, 1])

    magnitude = cv2.GaussianBlur(magnitude, (5, 5), 4)

    Fx = np.linspace(-magnitude.shape[1] / 2.,
                     magnitude.shape[1] / 2., magnitude.shape[1] + 1)
    k0 = 2 * np.pi / (res[1] * magnitude.shape[1])
    CDO_aux = np.arange(1, magnitude.shape[1] / 2.)
    CDO_array = 2 * np.pi / (CDO_aux * k0)
    K_scale = Fx * k0

    CDO_Mask = 500.
    Lmax = np.where(CDO_array < CDO_Mask)
    pix_max_mask = Lmax[0][0] + 1

    maskO = sector_mask(
        img.shape, (img.shape[0] / 2, img.shape[1] / 2), pix_max_mask, (0, 360))
    magnitude[maskO] = 0
    P2, max_freq = np.unravel_index(magnitude[:, magnitude.shape[0] / 2:].argmax(
    ), magnitude[:, magnitude.shape[0] / 2:].shape), magnitude[:, magnitude.shape[0] / 2:].argmax()

    x1, y1 = magnitude.shape[1] / 2, magnitude.shape[0] / 2
    p1 = [x1, -y1]
    p2 = [P2[1], P2[0]]  # p2=[x,y]

    p2[0], p2[1] = p2[0] + magnitude.shape[1] / 2, -p2[1]

    p2_plot = [p2[0], -p2[1]]

    Kscale = Fx * k0
    Kscale = Kscale[Kscale.shape[0] / 2 - 25:Kscale.shape[0] / 2 + 25 + 1]

    if p1 != p2:
        deltaY = p2[1] - p1[1]
        deltaX = p2[0] - p1[0]

        slope = rads2deg(np.arctan2(deltaY, deltaX))

        K_mag = np.sqrt((deltaX) * (deltaX) + (deltaY) * (deltaY))
        CDO = 2 * np.pi / (K_mag * k0)

        Dir = slope
        if (Dir >= 0. and Dir <= 90.):
            Dir = 90. - Dir
        elif (Dir > 90. and Dir <= 180.):
            Dir_aux = 180. - Dir
            Dir = 270. + Dir_aux
        elif Dir < 0.:
            Dir = 90. + (np.absolute(Dir))

        if verbose:
            print "\nWavelength: ", CDO
            print "Direction: ", Dir

        lon_aux1 = center[0]
        if lon_aux1 > 180.:
            lon_aux2 = lon_aux1 - 360.
        else:
            lon_aux2 = lon_aux1

        CDO_new = checkRacio(CDO, Tmax)
        lineOut = FFT_id + "   " + \
            str(lon_aux2) + "   " + \
            str(center[1]) + "   " + str(CDO_new) + "   " + str(Dir) + "\n"
        fout.write(lineOut)
    return CDO, Dir, magnitude, deltaX, deltaY, p2_plot, Kscale, pix_max_mask, CDO_array
##########################################################################################################################################################################


def GetBoxDim(res, DefaultDim=1000.):
    offset = int(round(((DefaultDim) / res)))
    offset = cv2.getOptimalDFTSize(offset)
    offset = np.int(round(offset / 2.))
    return offset


def GetOffset(CDOMax, res):
    offset = int(round(((CDOMax * 2) / res) / 2.))
    offset = cv2.getOptimalDFTSize(offset * 2)
    offset = np.int(round(offset / 2.))
    return offset


def GetFFTBox(Point, img, lon, lat, offset):
    img1 = img[Point[1] - offset:Point[1] + offset,
               Point[0] - offset:Point[0] + offset]
    lon1 = lon[Point[1] - offset:Point[1] + offset,
               Point[0] - offset:Point[0] + offset]
    lat1 = lat[Point[1] - offset:Point[1] + offset,
               Point[0] - offset:Point[0] + offset]
    img1 = scale_img(img1, 8)
    return img1, lon1, lat1


"""
def GetFFTBoxes(Point,img,lon,lat,offset):
    imgs, lats, lons= [],[],[]

    ##### P1
    P1=Point
    img1,lon1,lat1=	GetFFTBox(P1,img,lon,lat,offset)
    img1=scale_img(img1,8)

    ##### P2
    P2=(Point[0]-(offset/2),Point[1]-(offset/2))
    img2,lon2,lat2=	GetFFTBox(P2,img,lon,lat,offset)
    img2=scale_img(img2,8)

    ##### P3
    P3=(Point[0]-(offset/2),Point[1]+(offset/2))
    img3,lon3,lat3=	GetFFTBox(P3,img,lon,lat,offset)
    img3=scale_img(img3,8)

    ##### P4
    P4=(Point[0]+(offset/2),Point[1]+(offset/2))
    img4,lon4,lat4=	GetFFTBox(P4,img,lon,lat,offset)
    img4=scale_img(img4,8)

    ##### P5
    P5=(Point[0]+(offset/2),Point[1]-(offset/2))
    img5,lon5,lat5=	GetFFTBox(P5,img,lon,lat,offset)
    img5=scale_img(img5,8)

    imgs=[img1,img2,img3,img4,img5]
    lats=[lat1,lat2,lat3,lat4,lat5]
    lons=[lon1,lon2,lon3,lon4,lon5]
    return imgs,lons,lats
"""


def GetFFTBoxes(Point, img, lon, lat, offset, shift):
    imgs, lats, lons = [], [], []

    P_Grid = [(Point[0], Point[1]),
              (np.int(Point[0] - np.ceil(offset * shift)),
               np.int(Point[1] + np.ceil(offset * shift))),
              (np.int(Point[0]),	np.int(Point[1] + np.ceil(offset * shift))),
              (np.int(Point[0] + np.ceil(offset * shift)),
               np.int(Point[1] + np.ceil(offset * shift))),
              (np.int(Point[0] + np.ceil(offset * shift)),	np.int(Point[1])),
              (np.int(Point[0] + np.ceil(offset * shift)),
               np.int(Point[1] - np.ceil(offset * shift))),
              (np.int(Point[0]),	np.int(Point[1] - np.ceil(offset * shift))),
              (np.int(Point[0] - np.ceil(offset * shift)),
               np.int(Point[1] - np.ceil(offset * shift))),
              (np.int(Point[0] - np.ceil(offset * shift)),	np.int(Point[1]))]

    for i in P_Grid:
        img1, lon1, lat1 = GetFFTBox(i, img, lon, lat, offset)
        img1 = scale_img(img1, 8)
        imgs.append(img1)
        lons.append(lon1)
        lats.append(lat1)

    return imgs, lons, lats


def PlotSARFFT(img, lon1, lat1, CDO, DIR, mag, deltaX, deltaY, p2_plot, Kscale, RMask, CDO_array, FFT_id, CDOMax=500., zoom=25, dir="./FFT_outputs/"):

    offset = img.shape[0] / 2
    LonVec = lon1[0, :]
    LatVec = lat1[:, 0]

    Indexes = np.linspace(0, img.shape[0], 6)
    LON_aux = LonVec - 360.
    LON_labels = np.linspace(LON_aux[0], LON_aux[-1], 5)
    LAT_labels = np.linspace(LatVec[0], LatVec[-1], 5)

    LON_text = []
    for i in LON_labels:
        LON_text.append(str(round(i, 4)))

    LAT_text = []
    for i in LAT_labels:
        LAT_text.append(str(round(i, 4)))

    Kscale_text = []
    # print Kscale

    for i in Kscale:
        Kscale_text.append(str(round(i, 3)))
    Kscale_labels = [Kscale_text[0], Kscale_text[zoom / 2],
                     Kscale_text[zoom], Kscale_text[zoom + (zoom / 2) + 1], Kscale_text[-1]]
    fig1 = plt.figure(figsize=(15, 10))
    ax1 = fig1.add_subplot(121)
    ax1.imshow(img, cmap=plt.cm.gray)
    plt.quiver(img.shape[1] / 2, img.shape[0] / 2, deltaX, deltaY, color='r')
    plt.title("Wavelength: " + str(round(CDO, 2)) +
              "m \nSwell Direction: " + str(round(DIR, 2)) + "$^\circ$")
    ax1.set_xticks(Indexes)
    ax1.set_yticks(Indexes)
    ax1.set_xticklabels(LON_text, rotation=30)
    ax1.set_yticklabels(LAT_text)
    ax1.set_xlabel("Longitude")
    ax1.set_ylabel("Latitude")

    ax2 = fig1.add_subplot(122)
    ax2.imshow(mag, cmap=plt.cm.jet)
    plt.autoscale(False)
    plt.xlim(offset - zoom, offset + zoom)
    plt.ylim(offset + zoom, offset - zoom)
    plt.scatter(*p2_plot, color="b")
    ax2.set_xticks([offset - zoom, offset - (zoom / 2),
                    offset, offset + (zoom / 2), offset + zoom])
    ax2.set_yticks([offset + zoom, offset + (zoom / 2),
                    offset, offset - (zoom / 2), offset - zoom])
    ax2.set_xticklabels(Kscale_labels)
    ax2.set_yticklabels(Kscale_labels)
    ax2.set_xlabel("Kx (rad/m)")
    ax2.set_ylabel("Ky (rad/m)")
    plt.title("Spectral Magnitude")

    RMask = 0
    cMask = plt.Circle((offset, offset), RMask, color='k')

    Lmax = np.where(CDO_array < CDOMax)
    LambdaMAX = Lmax[0][0]
    cCDOMax = plt.Circle((offset, offset), LambdaMAX, color='w', fill=False)
    plt.text(offset - LambdaMAX, offset, str(np.int(CDOMax)) +
             "m", fontsize=8, color="w", fontweight="bold")

    CDOs = [200., 100., 50.]
    Lmax = []
    Lradii = []
    cCDOs = []
    for i in CDOs:
        Lmax.append(np.where(CDO_array < i))
        Lradii.append(Lmax[-1][0][0])
        if Lradii[-1] <= zoom:
            cCDO = plt.Circle((offset, offset),
                              Lradii[-1], color='w', fill=False)
            plt.text(offset - Lradii[-1], offset, str(np.int(i)) +
                     "m", fontsize=7, color="w", fontweight="bold")
            cCDOs.append(cCDO)

    # print "Raio CDOs:  ",Lradii
    fig = plt.gcf()
    fig.gca().add_artist(cMask)
    fig.gca().add_artist(cCDOMax)
    for n, i in enumerate(cCDOs):
        if Lradii[n] <= zoom:
            fig.gca().add_artist(i)

    plt.savefig(dir + FFT_id + ".png", dpi=100)
    plt.close()
    # plt.show()
    return None


def PlotSARFFT2(img, lon1, lat1, CDO, DIR, mag, deltaX, deltaY, p2_plot, Kscale, RMask, CDO_array, FFT_id, CDOMax=500., zoom=25, dir="./FFT_outputs/"):

    offset = img.shape[0] / 2
    LonVec = lon1[0, :]
    LatVec = lat1[:, 0]

    Indexes = np.linspace(0, img.shape[0], 6)
    LON_aux = LonVec - 360.
    LON_labels = np.linspace(LON_aux[0], LON_aux[-1], 5)
    LAT_labels = np.linspace(LatVec[0], LatVec[-1], 5)

    LON_text = []
    for i in LON_labels:
        LON_text.append(str(round(i, 4)))

    LAT_text = []
    for i in LAT_labels:
        LAT_text.append(str(round(i, 4)))

    Kscale_text = []
    print Kscale

    for i in Kscale:
        Kscale_text.append(str(round(i, 3)))
    Kscale_labels = [Kscale_text[0], Kscale_text[zoom / 2],
                     Kscale_text[zoom], Kscale_text[zoom + (zoom / 2) + 1], Kscale_text[-1]]
    fig1 = plt.figure(figsize=(15, 10))
    ax1 = fig1.add_subplot(121)
    ax1.imshow(img, cmap=plt.cm.gray)
    plt.quiver(img.shape[1] / 2, img.shape[0] / 2, deltaX, deltaY, color='r')
    plt.title("Wavelength: " + str(round(CDO, 2)) +
              "m \nSwell Direction: " + str(round(DIR, 2)) + "$^\circ$")
    ax1.set_xticks(Indexes)
    ax1.set_yticks(Indexes)
    ax1.set_xticklabels(LON_text, rotation=30)
    ax1.set_yticklabels(LAT_text)
    ax1.set_xlabel("Longitude")
    ax1.set_ylabel("Latitude")

    ax2 = fig1.add_subplot(122)
    ax2.imshow(mag, cmap=plt.cm.jet)
    plt.autoscale(False)
    plt.xlim(offset - zoom, offset + zoom)
    plt.ylim(offset + zoom, offset - zoom)
    plt.scatter(*p2_plot, color="b")
    ax2.set_xticks([offset - zoom, offset - (zoom / 2),
                    offset, offset + (zoom / 2), offset + zoom])
    ax2.set_yticks([offset + zoom, offset + (zoom / 2),
                    offset, offset - (zoom / 2), offset - zoom])
    ax2.set_xticklabels(Kscale_labels)
    ax2.set_yticklabels(Kscale_labels)
    ax2.set_xlabel("Kx (rad/m)")
    ax2.set_ylabel("Ky (rad/m)")
    plt.title("Spectral Magnitude")

    RMask = 0
    cMask = plt.Circle((offset, offset), RMask, color='k')

    Lmax = np.where(CDO_array < CDOMax)
    LambdaMAX = Lmax[0][0]
    cCDOMax = plt.Circle((offset, offset), LambdaMAX, color='w', fill=False)
    plt.text(offset - LambdaMAX, offset, str(np.int(CDOMax)) +
             "m", fontsize=8, color="w", fontweight="bold")

    CDOs = [200., 100., 50.]
    Lmax = []
    Lradii = []
    cCDOs = []
    for i in CDOs:
        Lmax.append(np.where(CDO_array < i))
        Lradii.append(Lmax[-1][0][0])
        if Lradii[-1] <= zoom:
            cCDO = plt.Circle((offset, offset),
                              Lradii[-1], color='w', fill=False)
            plt.text(offset - Lradii[-1], offset, str(np.int(i)) +
                     "m", fontsize=7, color="w", fontweight="bold")
            cCDOs.append(cCDO)

    # print "Raio CDOs:  ",Lradii
    fig = plt.gcf()
    # fig.gca().add_artist(cMask)
    # fig.gca().add_artist(cCDOMax)
    for n, i in enumerate(cCDOs):
        if Lradii[n] <= zoom:
            fig.gca().add_artist(i)

    plt.savefig(dir + FFT_id + ".png", dpi=100)
    plt.close()

    return None


def Plot_DTM(RunId, directory, graphics=False):
    data = np.loadtxt(directory + 'Depth_' + str(RunId) + '.txt')
    x, y, z = data[:, 1], data[:, 2], data[:, 5]

    zmax = math.ceil(np.nanmax(z))
    z[np.isnan(z)] = 200.

    xi = np.linspace(x.min(), x.max(), x.shape[0])
    yi = np.linspace(y.min(), y.max(), y.shape[0])
    zi = griddata((x, y), z.ravel(),
                  (xi[None, :], yi[:, None]), method='cubic')

    levs = np.linspace(0., zmax, 256)
    levs_x = np.linspace(0., zmax, 11)
    text_levs = text_labels(array_in=levs_x, form='3.0e')

    # plt.figure()
    # contours=plt.contourf(xi, yi, zi, levs, cmap=plt.cm.jet, norm=colors.BoundaryNorm(levs, ncolors=256, clip = False), origin='lower',aa=False)
    # cbar=plt.colorbar(contours,ticks=levs_x)
    # cbar.set_label('Depth (m)')
    # plt.savefig(directory+"Depth_"+str(RunId)+".png", dpi=300)
    if graphics:
        plt.show()
    return None


def CreateGTiFF(filein, fileout, EPSG=4326):
    f = gdal.Open(filein)
    a = f.GetRasterBand(1)
    img = f.ReadAsArray(0, 0, a.XSize, a.YSize).astype(np.uint16)
    Metadata = f.GetMetadata()
    ncols, nrows = a.XSize, a.YSize

    GCPs = f.GetGCPs()
    geotransform = f.GetGeoTransform()

    img = scale_img(img, 8)

    output_raster = gdal.GetDriverByName('GTiff').Create(
        fileout, ncols, nrows, 1, gdal.GDT_Byte)  # Open the file
    output_raster.SetGeoTransform(geotransform)  # Specify its coordinates
    srs = osr.SpatialReference()                 # Establish its coordinate encoding
    # This one specifies WGS84 lat long.
    srs.ImportFromEPSG(EPSG)
    # Exports the coordinate system
    output_raster.SetProjection(srs.ExportToWkt())
    # to the file
    output_raster.SetGCPs(GCPs, f.GetGCPProjection())
    output_raster.SetMetadata(Metadata)
    output_raster.GetRasterBand(1).WriteArray(
        img)   # Writes my array to the raster
    output_raster.GetRasterBand(1).SetNoDataValue(0)
    output_raster = None
    return None
