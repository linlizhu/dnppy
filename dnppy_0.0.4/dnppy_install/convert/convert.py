"""
======================================================================================
                                   dnppy.convert
======================================================================================
 This script is part of (dnppy) or "DEVELOP National Program py"
 It is maintained by the Geoinformatics YP class.

It contains functions for misc conversion between formats and types. 
"""



__all__=['HDF5',            # planned development
         'NetCDF',          # working with bugs
         'HDF',             # complete
         'date_to_julian',  # complete
         'julian_to_date']  # complete


# attempt to import all the common modules and settings
import arcpy,core,sys,os,time

if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    from arcpy.sa import *
    from arcpy import env
    arcpy.env.overwriteOutput = True
#========================================================================================


def HDF5(filelist, outdir=False):

    """
    Function extracts tifs from HDF5s such as IMERG, GMP data.

     inputs:
       filelist    list of '.hdf' files from which data should be extracted
       layerlist   list of layer numbers to pull out as individual tifs
       layernames  list of layer names to put more descriptive names to each layer
       outdir      directory to which tif files should be saved
                   if outdir is left as 'False', files are saved in the same directory as
                   the input file was found.
    """

    # import modules
    if core.check_module('h5py'): import h5py
    if core.check_module('numpy'): import numpy

    # set up lists
    failed=[]

    for filename in filelist:
        f = h5py.File(filename,'r')
        print '{HDF5} This function is unfinished!'

    return(failed)



def NetCDF(filelist,outdir,Quiet=False):

    """
     Function converts NetCDFs to tiffs. Designed to work with TRMM data.

     inputs:
       filelist    list of '.nc' files to conver to tifs.
       outdir      directory to which tif files should be saved

     Bugs:
       does not work with CMIP3 and CMIP5 netcdf's

     Authors: Fall2014: Jeffry Ely
    """

    # Set up initial parameters.
    arcpy.env.workspace = outdir
    filelist=core.Enforce_List(filelist)
    failed=[]

    # convert every file in the list "filelist"
    for infile in filelist:
        
        # use arcpy module to make raster layer from netcdf
        arcpy.MakeNetCDFRasterLayer_md(infile, "r", "longitude", "latitude", "r", "", "", "BY_VALUE")
        arcpy.CopyRaster_management("r", infile[:-3] + ".tif", "", "", "", "NONE", "NONE", "")
        if not Quiet:
            print '{NetCDF} Converted netCDF file ' + infile + ' to Raster'

                
    if not Quiet:print '{NetCDF} Finished!'     
    return (failed)



def HDF(filelist, layerlist, layernames=False, outdir=False, Quiet=False):

    """
     Function extracts tifs from HDFs.
     Use "Extract_MODIS_HDF" in the modis module for better
     handling of MODIS data with sinusoidal projections.

     inputs:
       filelist    list of '.hdf' files from which data should be extracted
       layerlist   list of layer numbers to pull out as individual tifs should be integers
                   such as [0,4] for the 0th and 4th layer respectively.
       layernames  list of layer names to put more descriptive names to each layer
       outdir      directory to which tif files should be saved
                   if outdir is left as 'False', files are saved in the same directory as
                   the input file was found.

     Authors: Fall2014: Jeffry Ely
    """


    # Set up initial arcpy modules, workspace, and parameters, and sanitize inputs.
    core.Check_Spatial_Extension()
    arcpy.env.overwriteOutput = True

    # enforce lists for iteration purposes
    filelist=core.Enforce_List(filelist)
    layerlist=core.Enforce_List(layerlist)
    layernames=core.Enforce_List(layernames)
    
    # ignore user input layernames if they are invalid, but print warnings
    if layernames and not len(layernames)==len(layerlist):
        print '{HDF} layernames must be the same length as layerlist!'
        print '{HDF} ommiting user defined layernames!'
        layernames=False

    # create empty list to add failed file names into
    failed=[]

    # iterate through every file in the input filelist
    for infile in filelist:
        # pull the filename and path apart 
        path,name = os.path.split(infile)
        arcpy.env.workspace = path

        for i in range(len(layerlist)):
            layer=layerlist[i]
            
            # specify the layer names.
            if layernames:
                layername=layernames[i]
            else:
                layername=str(layer).zfill(3)

            # use the input output directory if the user input one, otherwise build one  
            if outdir:
                if not os.path.exists(os.path.join(outdir,layername)):
                    os.makedirs(os.path.join(outdir,layername))
                outname=os.path.join(outdir,layername,name[:-4] +'_'+ layername +'.tif')
            else:
                if not os.path.exists(os.path.join(path,layername)):
                    os.makedirs(os.path.join(path,layername))
                outname=os.path.join(path,layername,name[:-4] +'_'+ layername +'.tif')

            # perform the extracting and projection definition
            try:
                # extract the subdataset
                arcpy.ExtractSubDataset_management(infile, outname, str(layer))
                
                if not Quiet:
                    print '{HDF} Extracted ' + outname
            except:
                if not Quiet:
                    print '{HDF} Failed extract '+ outname + ' from ' + infile
                failed.append(infile)
                
    if not Quiet:print '{HDF} Finished!' 
    return(failed)



def date_to_julian(year,month,day):

    """
    Converts a conventional date to julian day and year
    
     Inputs:
       year        the current year (maters for leap years). string or int
       month       the month of the year. string or int.
       day         the day of the month. string or int.

     Outputs:
       day         date-day for input julian day

     Example usage:
       for december 5th of the year you would type.
       julian_day = convert.date_to_julian(2014,12,5)
    """

    import datetime
    
    fmt = "%Y.%m.%d"
    info = datetime.datetime.strptime('.'.join([str(year),str(month),str(day)]),fmt)
    julian_day = info.strftime('%j')

    return(julian_day)



def julian_to_date(year,j_day):

    """
    Converts a julian day of the year to conventional date format.

     Inputs:
       year        the current year (maters for leap years)
       j_day       the julian day to convert to a date for given year

     Outputs:
       month       month of input julian day
       day         date-day for input julian day

     Example usage:
       for the 399th day of the year 2014 you would type
               month,day = convert.julian_to_date(2014,399)
    """
    
    import datetime
    
    fmt = "%Y.%j"
    info = datetime.datetime.strptime('.'.join([str(year),str(j_day)]),fmt)
    month = info.strftime('%m')
    day = info.strftime('%d')
    
    return(month,day)