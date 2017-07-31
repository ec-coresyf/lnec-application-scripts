#!/usr/bin/python2.7
# ==============================================================================
#                         <coresyf_calibration.py>
# ==============================================================================
# Project   : Co-ReSyF
# Company   : Deimos Engenharia
# Component : Co-ReSyF Tools (Radiometric Calibration)
# Language  : Python (v.2.6)
# ------------------------------------------------------------------------------
# Scope : Command line radiometric calibration for SNAP supported files
# Usage : (see the following docstring)
# ==============================================================================
# $LastChangedRevision:  $:
# $LastChangedBy:  $:
# $LastChangedDate:  $:
# ==============================================================================

""" SYSTEM AND PROGRAM MODULES """
import os
import zipfile
from argparse import ArgumentParser
from os import path
import shutil
import sys

from product_selector import ProductSelector
from gpt import call_gpt
from snapFileSelector import get_ProductFile
#sys.path.append('/home/coresyf/.snap/snap-python')


'''
@summary: 
TBC

@example:
TBC          

@attention: 
TBC

@version: v.1.0

@change:
1.0
- First release of the tool. 
'''

VERSION = '1.0'

DefaultAuxFilesLookup = ['Latest Auxiliary File', 'Product Auxiliary File', 'External Auxiliary File']


def main():
    parser = ArgumentParser(version=VERSION)

    # ==============================#
    # Define command line options  #
    # ==============================#
    parser.add_argument('--Ssource',
                        dest="Ssource", metavar='<filepath>',
                        help="Sets source to <filepath>",
                        required=True)
    parser.add_argument('--Pselector',
                        dest="Pselector", metavar='<glob>',
                        help="A glob to select the appropriate product files from a directory.")
    parser.add_argument('--Ttarget', metavar='<filepath>',
                        dest="Ttarget",
                        help="Sets the target to <filepath>")
    parser.add_argument('--PauxFile',
                        dest="PauxFile", metavar='<string>',
                        help="Value must be one of 'Latest Auxiliary File', 'Product Auxiliary File', "
                             "'External Auxiliary File'.",
                        default="Latest Auxiliary File",
                        choices=DefaultAuxFilesLookup)
    parser.add_argument('--PcreateBetaBand',
                        dest="PcreateBetaBand", metavar='<boolean>',
                        help="Create beta0 virtual band.",
                        type=bool,
                        default=False)
    parser.add_argument('--PcreateGammaBand',
                        dest="PcreateGammaBand", metavar='<boolean>',
                        help="Create gamma0 virtual band.",
                        default=False,
                        type=bool)
    parser.add_argument('--PexternalAuxFile',
                        dest="PexternalAuxFile", metavar='<file>',
                        help="The antenna elevation pattern gain auxiliary data file.")
    parser.add_argument('--PoutputBetaBand',
                        dest="PoutputBetaBand", metavar='<boolean>',
                        help="Output beta0 band.",
                        type=bool,
                        default=False)
    parser.add_argument('--PoutputGammaBand',
                        dest="PoutputGammaBand", metavar='<boolean>',
                        help="Output gamma0 band.",
                        type=bool,
                        default=False)
    parser.add_argument('--PoutputImageInComplex',
                        dest="PoutputImageInComplex", metavar='<boolean>',
                        help="Output image in complex.",
                        type=bool,
                        default=False)
    parser.add_argument('--PoutputImageScaleInDb',
                        dest="PoutputImageScaleInDb", metavar='<boolean>',
                        help="Output image scale.",
                        type=bool,
                        default=False)
    parser.add_argument("--PoutputSigmaBand", metavar='<boolean>',
                        dest="PoutputSigmaBand",
                        help="Output sigma0 band.",
                        type=bool,
                        default=True)
    parser.add_argument("--PselectedPolarisations", metavar='<string,string,string,...>',
                        dest="PselectedPolarisations",
                        help="The list of polarisations.",
                        default = "VV, VH")
    parser.add_argument("--PsourceBands", metavar='<string,string,string,...>',
                        dest="PsourceBands",
                        help="The list of source bands.",)

    opts = vars(parser.parse_args())

   # if not opts.Ssource:
   #     print("Readable input file not found!")
   #     return

    source = opts.pop("Ssource")
    #selector = opts.pop("Pselector")
    target = opts.pop("Ttarget")

    # if not os.path.exists(source):
    #     parser.error("%s does not exists." % source)
    # if path.isfile(source) and selector and not zipfile.is_zipfile(source):
    #     parser.error("Selectors should be used only for sources which are directories or zips.")
    # if path.isdir(source) and not selector:
    #     parser.error("Selector parameter is missing.")
    # if path.isdir(source) and target:
    #     parser.error("Target should not be specified when multiple source files are selected from a dir.")

    # ps = ProductSelector(selector)

    # ====================================#
    #  LOOP THROUGH ALL SELECTED PRODUCTS#
    # ====================================#
    # if path.isdir(source):
    #     product_files = [path.join(source, fname) for fname in os.listdir(source)
    #                      if ps.isproduct(path.join(source, fname))]
    #     print("selected files: %s%s" % (os.linesep, os.linesep.join(product_files)))
    # else:
    #     product_files = [source]

    # for i in product_files:
    #     print ("Applying calibration %s..." % i)

    checkZip = False
    if(zipfile.is_zipfile(source)):
        fileZip = zipfile.ZipFile(source)
        fileZip.extractall()
        currDir = os.getcwd()
        source = currDir + "/" + fileZip.namelist()[0] 
        checkZip = True
    else:
	source = get_ProductFile(source)

    #source = opts.Ssource
    #del opts.Ssource

    

    call_gpt('Calibration', source, target, opts)
    #if(checkZip):
     #   shutil.rmtree(tmpFolderName)

    # Workaoround to Wings naming conventions
    os.rename(target + ".tif", target)
if __name__ == '__main__':
    main()
