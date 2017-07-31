#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
from __future__ import division

"""
===============================================================================
Co-ReSyF Research Application - SAR_Bathymetry
===============================================================================
 Authors: 
 Date: June/2017
 Last update: June/2017
 
 Usage: ./CreateOutputGrid.py
 Example: ./CreateOutputGrid.py -o grid.txt --bbox -10 36 -9 37
 
 
 For help: ./CreateOutputGrid -h
===============================================================================

"""
from os.path import join, basename, dirname
from os import remove
import numpy as np
from osgeo import ogr
from pyproj import Proj, transform
import argparse
import zipfile
import uuid


class OutputGridCreator(object):
    def __init__(self, **kwargs):
        r'''
        Initializes an object to create an output grid

        :param \**kwargs:
            See below

        :Keyword Arguments:
            output_path: str
                The path to place the grid results
            bounding_box: list
                The bounding box for which the grid shall be calculated
            spacing : int, optional
                The spacing between grid points, in meters; defaults to 500
            inset : int, optional
                The inset on edge of grid in meters; defaults to 5
            crs_meters: str, optional
                The Coordinate Reference System to be used in meters; defaults to 3857
            crs_degrees: str, optional
                The Coordinate Reference System to be used in degrees; defaults to 4326
        '''
        if kwargs is not None:
            if kwargs['output'] is None:
                raise ValueError('Output path is undefined')
           
            if kwargs['bounding_box'] is None:
                raise ValueError('Bounding box is undefined')
            
            self.grid_params = kwargs
        
        else:
            raise ValueError('Input parameters are not defined')

    def degrees2meters(self, lon, lat):
        '''
        Converts a given lat/lon value, in degrees, to x/y, in meters
        '''
        proj_in = Proj(init='epsg:' + self.grid_params.get('crs_degrees'))
        proj_out = Proj(init='epsg:' + self.grid_params.get('crs_meters'))
        print lon
        print lat 
        x_meter, y_meter = transform(proj_in, proj_out, lon, lat)
        x_meter += self.grid_params.get('inset')
        y_meter += self.grid_params.get('inset')
        return x_meter, y_meter

    def meters2degrees(self, x, y):
        '''
        Converts a given x/y value, in meters, to lat/lon, in degrees
        '''
        proj_in = Proj(init='epsg:' + self.grid_params.get('crs_meters'))
        proj_out = Proj(init='epsg:' + self.grid_params.get('crs_degrees'))
        lon, lat = transform(proj_in, proj_out, x, y)
        return lon, lat

    def generate_lat_lon_vectors(self):
        '''
        Generates a latitude/longitude vector
        '''
        xmin, ymin = self.degrees2meters(float(self.grid_params.get('bounding_box')[0]),
                                         float(self.grid_params.get('bounding_box')[1]))
        xmax, ymax = self.degrees2meters(float(self.grid_params.get('bounding_box')[2]),
                                         float(self.grid_params.get('bounding_box')[3]))
 
        self.grid_params['lon_vector'] = [self.meters2degrees(x, ymax)[0] for x in (
                i for i in np.arange(xmin, xmax, int(self.grid_params.get('spacing'))))]
        self.grid_params['lat_vector'] = [self.meters2degrees(xmax, y)[1] for y in (
                i for i in np.arange(ymin, ymax, int(self.grid_params.get('spacing'))))]

    def generate_lat_lon_grid(self):
        self.grid_params['final_grid'] = []
        for val_lat in self.grid_params.get('lat_vector'):	
            for val_lon in self.grid_params.get('lon_vector'):		
                corrected_grid_values = [val_lon, val_lat]	
                self.grid_params['final_grid'].append(corrected_grid_values)
    
    def generate_final_output(self):
        grid_size = int(np.array(self.grid_params.get('final_grid')).size / 2)
        grid_filename = join(self.grid_params.get('output'), '%s_%i_final_grid_%s.txt' % (
            self.grid_params.get('prefix'), grid_size, uuid.uuid4().hex))
        out_file = open(grid_filename, 'w+')
        for lat_lon_pair in self.grid_params.get('final_grid'):
            out_file.write("%f\t%f\n" % (lat_lon_pair[0], lat_lon_pair[1]))
        out_file.close()

        return grid_size, grid_filename


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Co-ReSyF Grid Generator')
    parser.add_argument('-o', '--output', help='Output path for generated grids', required=True)
    parser.add_argument('-b', '--bbox', help='Bounding box to define grid extents', required=True)
    parser.add_argument('-p', '--prefix', help='Name prefix to append to output', default='', required=False)        
    parser.add_argument('-s', '--spacing', type=int, help='Input image', default=500, required=False)
    parser.add_argument('-m', '--crsm', help='Coordinate Reference System (for meters)', default='3857',
                        required=False)
    parser.add_argument('-d', '--crsd', help='Coordinate Reference System (for degrees)', default='4326',
                        required=False)
    parser.add_argument('-i', '--inset', type=int, help='Inset for grid edges', default=5, required=False)
    
    args = parser.parse_args()

    grid_creator = OutputGridCreator(
        output=args.output,
        bounding_box=args.bbox.split(),
        prefix=args.prefix,
        spacing=args.spacing,
        inset=args.inset,
        crs_meters=args.crsm,
        crs_degrees=args.crsd
    )

    grid_creator.generate_lat_lon_vectors()
    grid_creator.generate_lat_lon_grid()
    grid_output = grid_creator.generate_final_output()
    print(grid_output[0])
    print(grid_output[1])
