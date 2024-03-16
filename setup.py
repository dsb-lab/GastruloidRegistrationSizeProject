import SimpleITK as sitk
import matplotlib.pyplot as plt
import numpy as np
import skimage
import io
import os
import shutil
import argparse
import json
import pandas as pd
from progress.bar import Bar

#Parser
parser = argparse.ArgumentParser(
                    prog='Setup registration',
                    description='This script goes over the analysis and correction of a film.')

parser.add_argument('-f','--force',action='store_true',help="Remove any setup folder if it already exists and setup the analysis folder.")
parser.add_argument('-o','--output',action='store',help="Folder to use for saving the data.")
parser.add_argument('directory',help="Folder to store the data")

args = parser.parse_args()

# Global variables
directory = args.directory
directory_output = f"{directory}_output"

# Base arguments
def create_parameters_json(directory,directory_output):

    files = os.listdir(directory)

    reader = sitk.ImageFileReader()
    reader.SetFileName(f"{directory}/{files[0]}")
    reader.ReadImageInformation()

    return {

        "image_info" : {
            "voxel_size": reader.GetSpacing(),
            "first": 1,
            "last": len(files),
            "not_to_do": []
        },
        "preprocessing" : {
            "path_to_data": f"{directory}",
            "file_name": "XXXXX_{t:03d}.tif",
            "analysis_path": f"{directory_output}/preprocessing-analysis/",
            "projection_path": f"{directory_output}/preprocessing-projections/",
            "output_format": f"{directory_output}/preprocessing-files/preprocessed_"+"{t:03d}.tif",

            "analysis_samples":[1,len(files)],

            "cropping_cube":[
                [0,reader.GetSize()[0]],
                [0,reader.GetSize()[1]],
                [0,reader.GetSize()[2]]
            ],
            "n_hist_bins":100,
            "threshold":0,
            "saturation_percentile":99.999
        },
        "rigid" : {
            "path_to_data": f"{directory_output}/preprocessing-files/",
            "file_name": "preprocessed_{t:03d}.tif",
            "trsf_folder": f"{directory_output}/rigid-transformations/",
            "output_format": f"{directory_output}/rigid-files/rigid_"+"{t:03d}.tif",
            "projection_path": f"{directory_output}/rigid-projections/",
            "check_TP": 0,

            "compute_trsf": 1,
            "ref_TP": 1,
            "trsf_type": "rigid",
            "padding": 1,
            "recompute": 1,

            "apply_trsf": 1,
        },
        "nonlinear" : {
            "path_to_data": f"{directory_output}/rigid-files/",
            "file_name": "rigid_{t:03d}.tif",
            "trsf_folder": f"{directory_output}/nonlinear-transformations/",
            "output_format": f"{directory_output}/nonlinear-files/nonlinear_"+"{t:03d}.tif",
            "projection_path": f"{directory_output}/nonlinear-projections/",
            "check_TP": 0,

            "compute_trsf": 1,
            "ref_TP": 1,
            "trsf_type": "vectorfield",
            "padding": 1,
            "recompute": 1,

            "apply_trsf": 1,
        }
    }

def create_summary_csv(directory,directory_output):

    data = pd.DataFrame() 

    reader = sitk.ImageFileReader()

    with Bar('Reading metainformation from files...', max = len(os.listdir(directory))) as bar:
        for i,file in enumerate(np.sort(os.listdir(directory))):

            reader.SetFileName(f"{directory}/{file}")

            reader.ReadImageInformation()

            data.loc[i,'file'] = f"{directory}/{file}"
            data.loc[i,'dimensions'] = reader.GetDimension()
            data.loc[i,['X','Y','Z']] = reader.GetSize()
            data.loc[i,'channels'] = reader.GetNumberOfComponents()
            data.loc[i,'pixel_downsample'] = reader.GetDimension()
            data.loc[i,['spacing_X','spacing_Y','spacing_Z']] = reader.GetSpacing()

            bar.next()

    return data

# Functions
def setup_(directory,directory_output):

    print(f"Making new analysis folder in {directory_output}.")

    os.mkdir(directory_output)

    data = create_summary_csv(directory,directory_output)
    data.to_csv(f"{directory_output}/files.csv")

    json_object = json.dumps(create_parameters_json(directory,directory_output), indent=4)
    with open(f"{directory_output}/parameters.json", "w") as outfile:
        outfile.write(json_object)

def setup(directory,directory_output,force=False):
    """
    Make folder structure for the analysis from analysis.
    """
    if os.path.isdir(directory_output): #Check if folder exist
        if force: #If force, remove old and make new folrder
            print(f"Old analysis folder {directory_output} has been removed.")
            shutil.rmtree(directory_output)
            setup_(directory,directory_output)
        else: #If not force, raise exception
            raise Exception(f"Output folder '{directory_output}' for project '{directory}' exists, if you want to overwrite it, please, add the flag -f to foor overwritting.")
    else: #if it does not exist, make folder
        setup_(directory,directory_output)

# Script
if args.output:
    directory_output = args.output

if args.force:
    setup(directory,directory_output,force=True)
else:
    setup(directory,directory_output,force=False)