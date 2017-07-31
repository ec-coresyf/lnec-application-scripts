#!/usr/bin/env python
#==============================================================================
#                         <coresyf_vector_creator.py>
#==============================================================================
# Project   : Co-ReSyF
# Company   : Deimos Engenharia
# Component : Co-ReSyF Tools (vector editing and creation tool)
# Language  : Python (v.2.6)
#------------------------------------------------------------------------------
# Scope : Command line vector creation and edition tool for GDAL supported 
#         shapefiles.
# Usage : (see the following docstring)
#==============================================================================
# $LastChangedRevision:  $:
# $LastChangedBy:  $:
# $LastChangedDate:  $:
#==============================================================================

'''
@summary: 
This module runs the following Co-ReSyF tool:
 - Vector creation and edition
It uses the GDAL ogr module to create and edit shapefiles.
It can be used to create new shapefiles or to add attribute fields and respective 
values to existing shapefiles. Only the point geometry is supported. 

Refs: https://pcjericks.github.io/py-gdalogr-cookbook/geometry.html#create-a-point
      https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html

@example:

Example 1 - Create a shapefile using text file with data field values separated by tab character: 
./coresyf_vector_creator.py -o ../examples/VectorCreator/newshapefile.shp --data_file ../examples/VectorCreator/data_to_create.txt

Example 2 - Updating the previous shapefile with new data field values contained in 'data2.txt':
./coresyf_vector_creator.py -r ../examples/VectorCreator/newshapefile.shp --data_file ../examples/VectorCreator/data_to_edit.txt


@version: v.1.0
@author: RCCC

@change:
1.0
- First release of the tool. 
'''

VERSION = '1.0'
USAGE   = ( '\n'
            'coresyf_vector_creator.py.py [-r <InputVectorfile>] [-o <OutputVectorfile>] [--o_format <VectorFormat>] [--data_file <DataFile>]'
            "\n")


''' SYSTEM MODULES '''
from optparse import OptionParser
import sys
import csv, os


from osgeo import ogr, osr
import shutil
import time




def createPoint( point_coord = [] ):
    my_point = ogr.Geometry( ogr.wkbPoint )
    my_point.AddPoint(*point_coord)     
    
    print my_point.ExportToWkt()
    return my_point
    
    
def createLine( line_coord = [] ):
    my_line = ogr.Geometry( ogr.wkbLineString )
    for point_coord in line_coord:
        my_line.AddPoint(*point_coord)
    
    print my_line.ExportToWkt()
    return my_line 


def createLinearRing( line_coord = [] ):
    my_ring = ogr.Geometry( ogr.wkbLinearRing )
    for point_coord in line_coord:
        my_ring.AddPoint(*point_coord)
    
    print my_ring.ExportToWkt()
    return my_ring


def createMultiPoint( points_coord = [] ):
    my_multipoint = ogr.Geometry( ogr.wkbMultiPoint )
    for point_coord in points_coord:
        my_multipoint.AddGeometry( createPoint(point_coord) )
     
    print my_multipoint.ExportToWkt()
    return my_multipoint


def createMultiLine( lines_coord = [] ):
    my_multiline = ogr.Geometry( ogr.wkbMultiLineString )
    for line_coord in lines_coord:
        my_multiline.AddGeometry( createLine(line_coord) )
     
    print my_multiline.ExportToWkt()
    return my_multiline


def createPolygon( points_coord = [] ):
    my_polygon = ogr.Geometry( ogr.wkbPolygon )
    my_polygon.AddGeometry( createLinearRing(points_coord) )
     
    print my_polygon.ExportToWkt()
    return my_polygon
 
def createMultiPolygon( polygons_coord = [] ):
    my_multipolygon = ogr.Geometry( ogr.wkbMultiPolygon )
    for polygon_coord in polygons_coord:
        my_multipolygon.AddGeometry( createPolygon(polygon_coord) )
     
    print my_multipolygon.ExportToWkt()
    return my_multipolygon
     
#createPoint([10, 20])                                                                   # POINT (10 20 0)   
#createLine([[10, 20], [30, 40]])                                                        # LINESTRING (10 20 0,30 40 0)    
#createPolygon([[10, 20], [30, 40], [60, 70]])                                           # POLYGON ((10 20 0,30 40 0,60 70 0))
#createMultiPoint([[10, 20], [30, 40], [60, 70]])                                        # MULTIPOINT (10 20 0,30 40 0,60 70 0)
#createMultiLine([ [[10, 20], [30, 40], [60, 70]], [[10, 20], [30, 40], [60, 70]] ])     # MULTILINESTRING ((10 20 0,30 40 0,60 70 0),(10 20 0,30 40 0,60 70 0))
#createMultiPolygon([ [[10, 20], [30, 40], [60, 70]], [[10, 20], [30, 40], [60, 70]] ])  # MULTIPOLYGON (((10 20 0,30 40 0,60 70 0)),((10 20 0,30 40 0,60 70 0)))


def createGeoFromWKT (wkt_code):    
    geo = ogr.CreateGeometryFromWkt(wkt_code)
    if geo:
        return geo
    else:
        print ('WKT Expression Error. Check syntax')

#createGeoFromWKT('POINT (10 0)')


def createVector(file_path, data_file, format_name='ESRI Shapefile' ):
    # this is a wings workaround since wings does not name files with extensions
    #file_path = file_path + ".shp"
    # set up the shapefile driver
    output_file_path = file_path
    file_path = "/tmp/Bathymetry"
    driver = ogr.GetDriverByName( format_name )
    # Remove output shapefile if it already exists
    if os.path.exists(file_path):
        driver.DeleteDataSource(file_path)
    # create the data source
    dst_datasource = driver.CreateDataSource( file_path + ".shp" )
    # Create layer with the spatial reference, WGS84
    proj = osr.SpatialReference()
    proj.SetWellKnownGeogCS( 'EPSG:4326' )
    layer_name = "Bathymetry"
    dst_layer = dst_datasource.CreateLayer(layer_name, srs=proj, geom_type = ogr.wkbPoint)
    
    # Read data from data file
    data = csv.DictReader(open(data_file,"rb"), delimiter=',', quoting=csv.QUOTE_NONE)
    
    # Add a new fields
    for field in data.fieldnames:
        new_field = ogr.FieldDefn(field, ogr.OFTReal)
        dst_layer.CreateField(new_field)
        new_field = None
    # Add features and attributes to the shapefile
    for row in data:
        feature = ogr.Feature ( dst_layer.GetLayerDefn() )
        for field in data.fieldnames:
            feature.SetField(field, row[field])
        # create the geometry from WKT
        wkt = "POINT(%f %f)" %  (float(row['Longitude']) , float(row['Latitude']))
        point = ogr.CreateGeometryFromWkt(wkt)    
        feature.SetGeometry( point )
        dst_layer.CreateFeature(feature)
        feature = None
    # end of the workaround. Now a file with shapefile contents is saved in the filepath that wings provided
    #os.rename(file_path, file_path_temp)
    dst_datasource = None

    shutil.move(file_path + ".shp", output_file_path)
    shutil.move(file_path + ".dbf", output_file_path + ".dbf")
    shutil.move(file_path + ".prj", output_file_path + ".prj")
    shutil.move(file_path + ".shx", output_file_path + ".shx")
        
#createVector('/home/rccc/_CORESYF/coresyf_toolkit/examples/VectorCreator/myshape.shp', '/home/rccc/_CORESYF/coresyf_toolkit/examples/VectorCreator/data_to_create.txt')


def editVector(file_path, data_file, format_name='ESRI Shapefile' ):
    print "PASSEI AQUI"
    # set up the shapefile driver
    driver = ogr.GetDriverByName( format_name )
    # Open the data source
    inDataSource = driver.Open(file_path, 1) # 0 means read-only. 1 means writable.
    
    # Get layer
    inLayer = inDataSource.GetLayer()
    
    # Read data from data file
    data = csv.DictReader(open(data_file,"rb"), delimiter='\t', quoting=csv.QUOTE_NONE)
    
    # Add a new fields
    for field in data.fieldnames:
        new_field = ogr.FieldDefn(field, ogr.OFTReal)
        inLayer.CreateField(new_field)
        new_field = None
    
    # Add features and attributes to the shapefile
    inFeature = inLayer.GetNextFeature()
    for row in data:
        for field in data.fieldnames:
            inFeature.SetField(field, row[field])
        inLayer.SetFeature(inFeature)
        inFeature = inLayer.GetNextFeature()
        if not inFeature: break
        
#editVector('/home/rccc/_CORESYF/coresyf_toolkit/examples/VectorCreator/myshape.shp', '/home/rccc/_CORESYF/coresyf_toolkit/examples/VectorCreator/data_to_edit.txt')



def main():
    parser = OptionParser(usage   = USAGE, 
                          version = VERSION)
    
    #==============================#
    # Define command line options  #
    #==============================#
    parser.add_option('-r', 
                      dest="input_file", metavar=' ',
                      help="input file for editing (GDAL supported vector file)"
                           "use this option to update an existing vector file" , )
    parser.add_option('-o', 
                      dest="output_file", metavar=' ',
                      help=("output vector file to be created (default: 'output_vector.shp')"
                            "use this option to create a new vector file"),
                      default="output_vector.shp")
    parser.add_option('--o_format', 
                      dest="output_format", metavar=' ',
                      help= ("GDAL vector format for output file, some possible formats are"
                             " 'ESRI Shapefile', 'netCDF'  (default: 'ESRI Shapefile')"),
                      default="ESRI Shapefile" )
    parser.add_option('--data_file', 
                      dest="data_file", metavar=' ',
                      help= ("Delimited text file with data fields separated by tab character"),
                      )    


    #==============================#
    #   Check mandatory options    #
    #==============================#
    (opts, args) = parser.parse_args()
    
    if len(sys.argv) == 1:
        print(USAGE)
        return
    if not opts.input_file and not opts.output_file:
        print("No vector file provided for editing or output file to be created. Nothing to do!")
        print(USAGE)
        return
    if not opts.data_file:
        print("No data file provided containing the field values. Nothing to do!")
        print(USAGE)
        return
    if opts.input_file and not os.path.exists(opts.input_file):
        print("The vector file %s was not found. No vector file available for editing!" % opts.input_file)
        return
    
    #==========#
    #   Run    #
    #==========#    
    try:
        if opts.input_file:
            print ("\nUpdating vector file using data from %s ..." % opts.data_file)
            editVector(opts.input_file, opts.data_file)
        else:
            print ("\nCreating a new vector file using data from %s ..." % opts.data_file)
            createVector(opts.output_file, opts.data_file, opts.output_format)
        print ('...Done!')    
    except Exception as message:
        print( str(message) )
        print('Error: Unable to create or edit vector file.')
        sys.exit(-1)

if __name__ == '__main__':   
    main()
