#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
===============================================================================
Co-ReSyF Research Application - SAR_Bathymetry
===============================================================================

===============================================================================
"""

import os
import argparse



########## Input arguments
parser = argparse.ArgumentParser(description='Co-ReSyF: Sar Bathymetry merging tool')
parser.add_argument('-i', '--input', nargs='+', help='List of Input text files...', required=True)
parser.add_argument('-o', '--output', help='Output file text file... ', required=True)
args = parser.parse_args()


files_list=args.input

output_file = open(args.output, 'w')

output_buffer = []

for i in range (0, len(files_list)):
    input_file = open(files_list[i], 'r')
    output_buffer.append(input_file.readline().replace('   ', ','))
    input_file.close()

output_buffer.sort()
output_file.write("ID,Longitude,Latitude,CDO_mean,DIR_mean,Depth\n")          #output_file.write("ID\tLongitude\tLatitude\tCDO_mean\tDIR_mean\tDepth\n")
for j in range (0, len(output_buffer)):
    output_file.write(output_buffer[j])

output_file.close()

# Delete the input .txt files 
for i in range (0, len(files_list)):
    os.remove(files_list[i])