#!/usr/bin/env python
#==============================================================================
#                         <coresyf_speckle_filter.py>
#==============================================================================
# Project   : Co-ReSyF
# Company   : Deimos Engenharia
# Component : Co-ReSyF Tools (Speckle Filter)
# Language  : Python (v.2.6)
#------------------------------------------------------------------------------
# Scope : Command line tool for applying SAR speckle filter
# Usage : (see the following docstring)
#==============================================================================
# $LastChangedRevision:  $:
# $LastChangedBy:  $:
# $LastChangedDate:  $:
#==============================================================================

'''
@summary: 
This module runs the following Co-ReSyF tool:
 - SPECKLE FILTER
Speckle is caused by random constructive and destructive interference resulting
in salt and pepper noise throughout the image. Speckle filters can be applied 
to the data to reduce the amount of speckle at the cost of blurred features
or reduced resolution.
It uses the command line based Graph Processing Tool (GPT) to apply speckle
filter to SAR input images. The input can be a single image or a directory
with several images.


@example:
Example 1 - Apply Speckle Median filter to RADARSAT product and save the output into
            user-defined path.
./coresyf_speckle_filter.py -s /RS2_OK871_PK6637_DK3212_SCWA_20080426_141717_HH_HV_SGF/product.xml 
                            --Pfilter="Median" --Ttarget=myoutput


Example 2 - The previous example, however in this case the user provides as input the product folder:
./coresyf_speckle_filter.py -s /Vancouver_R2_FineQuad15_Frame2_SLC 
                            --Pfilter="Median" --Ttarget=myoutput

@attention: 
  @todo: 
  - test all features and parameters?


@version: v.1.0
@author: RCCC

@change:
1.0
- First release of the tool. 
'''

VERSION = '1.0'
USAGE   = ( '\n'
            'coresyf_speckle_filter.py [-s <Inputdatasource>] [--Ttarget=<OutputDataPath>]\n'
            "                          [--PdampingFactor=<DampingValue>] [--PedgeThreshold=<EdgeThreshold>]\n"
            "                          [--Penl=<LooksNumber>] [--PestimateENL=<Boolean>]\n"
            '                          [--Pfilter=<FilterName>] [--PfilterSizeX=<KernelXdimension>] [--PfilterSizeY=<KernelYdimension>]\n'
            '                          [--PsourceBands="<BandName1>,<BandName2>,..."]'
            "\n")  

FilterNames  = [ 'None', 'Boxcar', 'Median', 'Frost', 'Gamma Map', 'Lee', 'Refined Lee', 'Lee Sigma', 'IDAN']
BoolOptions = ['false', 'true']


''' SYSTEM MODULES '''
from optparse import OptionParser
import sys
import os
import shutil
import gc

''' PROGRAM MODULES '''
from gpt import call_gpt
from snapFileSelector import get_ProductFile
import zipfile


def main():
    parser = OptionParser(usage   = USAGE, 
                          version = VERSION)

    #==============================#
    # Define command line options  #
    #==============================#
    parser.add_option('-s', 
                      dest="Ssource", metavar=' ',
                      help="input SAR file",)
    parser.add_option('--Ttarget', metavar=' ',
                      dest="Ttarget",
                      help="Sets the output file path")
    parser.add_option('--PdampingFactor',
                      dest="PdampingFactor", metavar=' ',
                      help=("The damping factor (Frost filter only) "
                            "Valid interval is (0, 100). Default value is 2.") ,
                     # default="2",
                      type=int)
    parser.add_option('--PedgeThreshold', 
                      dest="PedgeThreshold", metavar=' ',
                      help=("The edge threshold (Refined Lee filter only)"
                            "Valid interval is (0, *). Default value is 5000."),
                      #default="5000",
                      type=float, )
    parser.add_option('--Penl', 
                      dest="Penl", metavar=' ',
                      help=("The number of looks. Valid interval is (0, *)."
                            "Default value is 1.0."),
                     # default="1.0",
                      type=float)
    parser.add_option('--PestimateENL', 
                      dest="PestimateENL", metavar=' ',
                      help=("Sets parameter 'estimateENL' to <boolean>. "
                            "Default value is 'false'."),
                      type='choice', choices=BoolOptions,
                      #default="false",
                      )
    parser.add_option('--Pfilter', 
                      dest="Pfilter", metavar=' ',
                      help=("Parameter filter name."
                            "Value must be one of: %s ."
                            "Default value is 'None'.") % FilterNames,
                      type='choice', choices=FilterNames,
                      #default="None", 
                      )
    parser.add_option('--PfilterSizeX',
                      dest="PfilterSizeX", metavar=' ',
                      help=("The kernel x dimension. Valid interval is (1, 100]."
                            "Default value is '3'"),
                      #default="3",
                      type=int)
    parser.add_option('--PfilterSizeY',
                      dest="PfilterSizeY", metavar=' ',
                      help=("The kernel y dimension. Valid interval is (1, 100]."
                            "Default value is '3'"),
                      #default="3",
                      type=int)
    parser.add_option('--PsourceBands',
                      dest="PsourceBands", metavar=' ',
                      help="The list of source bands.",
                      default = "Sigma0_VV",
                      )
    
    
    #==============================#
    #   Check mandatory options    #
    #==============================#
    (opts, args) = parser.parse_args()
    
    if len(sys.argv) == 1:
        print(USAGE)
        return
    if not opts.Ssource:
        print("No input file provided. Nothing to do!")
        print(USAGE)
        return

    checkZip = False
    if(zipfile.is_zipfile(opts.Ssource)):
        fileZip = zipfile.ZipFile(opts.Ssource)
        fileName = fileZip.namelist()[0]
        fileZip.extractall()
        #currDir = os.getcwd()
        opts.Ssource = currDir + "/" + fileName
        checkZip = True
    else:
        # This is a wings workaround
        os.rename(opts.Ssource, opts.Ssource + ".tif")
        opts.Ssource = get_ProductFile(opts.Ssource + ".tif")
    if not opts.Ssource:
        print("Readable input file not found!")
        return

    #===============================#
    # Remove non-applicable options #
    #===============================#
    if opts.Pfilter != 'Frost':
        del opts.PdampingFactor

    if opts.Pfilter != 'Refined Lee':
        del opts.PedgeThreshold

    source = opts.Ssource
    del opts.Ssource

    target = ''
    if opts.Ttarget:
        target = opts.Ttarget
        del opts.Ttarget

    #============================#
    #    Run gpt command line    #
    #============================#
    call_gpt('Speckle-Filter', source, target, vars(opts))
    #if(checkZip):
    #    shutil.rmtree(tmpFolderName)

    # This is a wings workaround to naming convention
    if(checkZip == False):
        os.rename(source, source[:-4])
    os.rename(target + ".tif", target)
if __name__ == '__main__':
    main()
