#!/usr/bin/env python
#==============================================================================
#                         <snapFileSelector.py>
#==============================================================================
# Project   : Co-ReSyF
# Company   : Deimos Engenharia
# Component : Co-ReSyF Tools (Snap Files Selector)
# Language  : Python (v.2.7)
#------------------------------------------------------------------------------
# Scope : (see the following docstring)
# Usage : python snapFileSelector.py
#==============================================================================
# $LastChangedRevision:  $:
# $LastChangedBy:  $:
# $LastChangedDate:  $:
#==============================================================================

'''
This module recognizes and differentiates the file formats that SNAP can handle.

It will be used to automatically identify which file(s) should be open by the
GPT tool. Geotiff and NetCDF files are considered auxiliary files and are only
returned if no other Snap readable file is found.

------------------------------------------------------------------------------
@info
Adapted from: 
http://remote-sensing.eu/preprocessing-of-sentinel-1-sar-data-via-snappy-python-module/
https://github.com/senbox-org/snap-examples/blob/master/snap-engine-python-scripts/src/main/python/ndvi_processor_34.py

SNAP Engine API documentation:
http://step.esa.int/docs/v5.0/apidoc/engine/

SNAP examples:
https://github.com/senbox-org/snap-engine/blob/master/snap-python/src/main/resources/snappy/examples/ 

@version: v.1.0
@author: RCCC

@note_1: Creating symbolic links resolves issue/warning with reading product files (OPTIONAL): 
         SNAP_HOME=~/snap
         cd $SNAP_HOME/snap/modules/lib/x86_64
         ln -s ../amd64/libjhdf.so
         ln -s ../amd64/libjhdf5.so
         
@note_2: SNAP GUI has a option at "File >> Product Library" that recursively scans directories
        and retrieves all product files. A more complex and complete selection tool may be based
        in: 
https://github.com/senbox-org/snap-desktop/blob/f44c193e60c735833d814e1c909e1db077e69991/snap-product-library/src/main/java/org/esa/snap/productlibrary/rcp/toolviews/DBScanner.java
    
'''

__version__ = '1.0'

''' PROGRAM MODULES '''
import snappy
print('snappy.__file__:', snappy.__file__)
from snappy import jpy
from snappy import ProductIO

''' SYSTEM MODULES '''
import sys
import os
sys.path.append( os.path.expanduser("~") + '/.snap/snap-python')


''' IMPORTANT PARAMETERS '''
AUX_DATA_FILES = ['GeoTIFF', 'GeoTIFF-BigTIFF', 'NetCDF'] 




#====================================#
#    DISABLING SNAP LOG MESSAGES     #
#====================================#
Logger = jpy.get_type('java.util.logging.Logger')
Level  = jpy.get_type('java.util.logging.Level')

Logger.getLogger('').setLevel(Level.OFF)
snappy.SystemUtils.LOG.setLevel(Level.OFF)


#===================================#
#  GET SNAP PRODUCT FILE FUNCTION   #
#===================================#
def get_ProductFile( p_path ):
    
    files = []
    if(os.path.isfile(p_path)):
        print("Checking if the file is readable by snap:\n %s ..." % p_path )
        files.append(p_path)
    else:
        print("Finding snap product file at directory:\n %s ..." % p_path )
        files.extend( [os.path.join(p_path, fa) for fa in os.listdir(p_path) 
                                           if os.path.isfile( os.path.join(p_path, fa) )] )
    p_file_aux = None
    for fi in files: 
        p = None
        try:
            # Reads data product. The method does not automatically read band data
            p = ProductIO.readProduct(fi)
        except:
            pass
        
        if p:
            p_type = p.getProductType()
            if p.getProductType() in AUX_DATA_FILES:
                p_file_aux = fi
            else:
                print(' ------------------------------------------------')
                print(' Type: '       + p.getProductType() )
                print(' Mission/Format: '     + ', '.join( p.getProductReader().getReaderPlugIn().getFormatNames() ))
                #print(' Band Names: ' + ', '.join( p.getBandNames() ) )
                #print(' Raster Sizes: heigth=%d, Width=%d' % (p.getSceneRasterHeight(), p.getSceneRasterWidth()) )
                print(' ------------------------------------------------')
                return fi
    
    return p_file_aux
        
        
        



if __name__ == '__main__':
    
    # Test products
    PRODUCTS_DIR = "/home/rccc/Downloads/TEMP_SAR_PRODUCTS/"
    RADARSAT2_DIR = '/home/rccc/Downloads/TEMP_SAR_PRODUCTS/Vancouver_R2_FineQuad15_Frame2_SLC/'
    SENT3_DIR = '/home/rccc/Downloads/TEMP_SAR_PRODUCTS/S3A_SL_1_RBT____20170202T140355_20170202T140655_20170202T150744_0179_014_039_0539_SVL_O_NR_002.SEN3/'
    SENT2_DIR = '/home/rccc/Downloads/TEMP_SAR_PRODUCTS/S2A_MSIL1C_20170202T090201_N0204_R007_T34QGF_20170202T091143.SAFE/'
    SENT1_DIR = '/home/rccc/Downloads/TEMP_SAR_PRODUCTS/S1B_EW_GRDM_1SDH_20170202T133833_20170202T133937_004122_007219_D680.SAFE/'
    
    product_file = get_ProductFile(SENT1_DIR)
    print("\nProduct file is:")
    print( product_file )



