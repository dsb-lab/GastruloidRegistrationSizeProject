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
import re
from itertools import takewhile

#Parser
parser = argparse.ArgumentParser(
                    prog='Setup registration',
                    description='This script goes over the analysis and correction of a film.')

parser.add_argument('-f','--force',action='store_true',help="Remove any setup folder if it already exists and setup the analysis folder.")
parser.add_argument('-o','--output',action='store',help="Folder to use for saving the data.")
parser.add_argument('-s','--skip',action='store_true',help="Skip preprocessing.")
parser.add_argument('-p','--pattern',action='store',help="Only count files with this.")
parser.add_argument('directory',help="Folder to store the data")

args = parser.parse_args()

# Global variables
directory = args.directory
if directory[-1] == "/":
    directory = directory[:-1]
directory_output = f"{directory}_output"

# Base arguments
def create_parameters_json(directory,directory_output,skip):

    l = [i for i in os.listdir(directory) if args.pattern in i]
    name_pattern = detect_pattern(l) #Detect pattern
    min_, max_ = find_min_max(l) #Detect min and max names
    not_to_do = list(find_missing_elements(l)[0]) #Get list of elements not present in dataset
    # remove any element with weird shape
    d = pd.read_csv(f"{directory_output}/files.csv")
    for feature in ["dimensions","X","Y","Z","channels","pixel_downsample","spacing_X","spacing_Y","spacing_Z"]:
        median_ = d[feature].median()
        not_to_do += list(np.where(d[feature].values != median_)[0])
    not_to_do = list(np.unique(not_to_do))

    files = os.listdir(directory)

    reader = sitk.ImageFileReader()
    reader.SetFileName(f"{directory}/{files[0]}")
    reader.ReadImageInformation()

    json_file = {

        "image_info" : {
            "voxel_size": reader.GetSpacing(),
            "first": min_,
            "last": max_,
            "not_to_do": not_to_do,
            "low_th": 0,
        },
        "preprocessing" : {
            "path_to_data": f"{directory}",
            "file_name": name_pattern,
            "analysis_path": f"{directory_output}/preprocessing-analysis/",
            "projection_path": f"{directory_output}/preprocessing-projections/",
            "output_format": f"{directory_output}/preprocessing-files/preprocessed_"+"{t:03d}.tif",

            "analysis_samples":[min_, max_],

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
            "keep_vectorfield": 1
        }
    }

    if skip:
        json_file["rigid"]["path_to_data"] = json_file["preprocessing"]["path_to_data"]
        json_file["rigid"]["file_name"] = json_file["preprocessing"]["file_name"]
        del json_file["preprocessing"]

    return json_file

def create_summary_csv(directory,directory_output):

    data = pd.DataFrame() 

    reader = sitk.ImageFileReader()

    l = [i for i in os.listdir(directory) if args.pattern in i]
    with Bar('Reading metainformation from files...', max = len(l)) as bar:
        for i,file in enumerate(np.sort(l)):

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
def setup_(directory,directory_output,skip):

    print(f"Making new analysis folder in {directory_output}.")

    os.mkdir(directory_output)

    data = create_summary_csv(directory,directory_output)
    data.to_csv(f"{directory_output}/files.csv")

    json_object = json.dumps(create_parameters_json(directory,directory_output,skip), indent=4)
    with open(f"{directory_output}/parameters.json", "w") as outfile:
        outfile.write(json_object)

def setup(directory,directory_output,skip,force=False):
    """
    Make folder structure for the analysis from analysis.
    """
    if os.path.isdir(directory_output): #Check if folder exist
        if force: #If force, remove old and make new folrder
            print(f"Old analysis folder {directory_output} has been removed.")
            shutil.rmtree(directory_output)
            setup_(directory,directory_output,skip)
        else: #If not force, raise exception
            raise Exception(f"Output folder '{directory_output}' for project '{directory}' exists, if you want to overwrite it, please, add the flag -f to foor overwritting.")
    else: #if it does not exist, make folder
        setup_(directory,directory_output,skip)

def detect_pattern(filenames):
    # Helper function to find common prefix
    def common_prefix(strings):
        return ''.join(c[0] for c in takewhile(lambda x: all(x[0] == y for y in x), zip(*strings)))

    # Helper function to find common suffix
    def common_suffix(strings):
        reversed_strings = [s[::-1] for s in strings]
        reversed_suffix = common_prefix(reversed_strings)
        return reversed_suffix[::-1]

    if not filenames:
        raise ValueError("No filenames provided.")
    
    # Find common prefix and suffix
    prefix = common_prefix(filenames)
    suffix = common_suffix(filenames)
    
    # Extract the variable part by removing the common prefix and suffix
    variable_parts = [filename[len(prefix):-len(suffix)] for filename in filenames]
    
    # Ensure all variable parts are numeric and determine the length of the numeric part
    if not all(part.isdigit() for part in variable_parts):
        raise ValueError("Variable parts are not all numeric.")
    
    variable_length = len(variable_parts[0])
    if not all(len(part) == variable_length for part in variable_parts):
        raise ValueError("Variable numeric parts have different lengths.")
    
    # Construct the generalized pattern
    generalized_pattern = f"{prefix}{{t:0{variable_length}d}}{suffix}"
    
    return generalized_pattern


def find_min_max(filenames):
    # Extract the pattern
    pattern = detect_pattern(filenames)
    
    # Find the positions of the variable numeric part
    prefix, suffix = pattern.split("{t:", 1)[0], pattern.split("}")[1]
    
    # Extract the variable parts based on detected pattern
    variable_parts = [int(filename[len(prefix):-len(suffix)]) for filename in filenames]
    
    # Find the minimum and maximum values
    min_value = min(variable_parts)
    max_value = max(variable_parts)
    
    return min_value, max_value

def find_missing_elements(filenames):
    min_value, max_value = find_min_max(filenames)
    pattern = detect_pattern(filenames)
    
    # Extract the variable parts using regex
    regex = re.compile(r'\d+')
    variable_parts = [int(regex.search(filename).group()) for filename in filenames]
    
    # Generate the full range of numbers between min and max
    full_range = set(range(min_value, max_value + 1))
    
    # Identify the missing elements
    existing_elements = set(variable_parts)
    missing_elements = sorted(full_range - existing_elements)
    
    # Generate the filenames for the missing elements using the pattern
    missing_filenames = [pattern.format(t=missing) for missing in missing_elements]
    
    return missing_elements, missing_filenames

# Script
if args.output:
    directory_output = args.output
    if directory_output[-1] == "/":
        directory_output = directory_output[:-1]

if args.force:
    setup(directory,directory_output,args.skip,force=True)
else:
    setup(directory,directory_output,args.skip,force=False)
