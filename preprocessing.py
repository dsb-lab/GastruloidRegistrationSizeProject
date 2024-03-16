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
                    prog='Preprocessing',
                    description='This script goes over the preprocessing of the rigid correction.')

parser.add_argument('-a','--analysis',action='store_true',help="Make a preliminar sampling.")
parser.add_argument('-x','--execute',action='store_true',help="Execute the analysis.")
parser.add_argument('-c','--clean',action='store_true',help="Clean folders.")
parser.add_argument('parameters',help="Parameters file of the experiment.")

args = parser.parse_args()

#Parameters
with open(args.parameters,"r") as file:
    parameters_ = json.load(file)
    parameters = {}
    for i,j in parameters_["image_info"].items():
        parameters[i] = j
    for i,j in parameters_["preprocessing"].items():
        parameters[i] = j

# Preprocessing pipeline
def preprocessing(image,file,parameters):

    #Copy image
    image_preprocessed = sitk.Image(image)
    #Preprocessing has to be performed over the sitk object
        #Threshold
    image_preprocessed[image<parameters["threshold"]] = 0

        #Threshold Plot
    if args.analysis: #Only plot during analysis
        pixels = sitk.GetArrayFromImage(image).flatten()
        max_ = np.percentile(pixels,parameters["saturation_percentile"])

        fig_hist,ax_hist = plt.subplots(1,1,figsize=(10,5))
        counts = ax_hist.hist(pixels,bins=parameters["n_hist_bins"])[0]
        ax_hist.vlines(parameters["threshold"],0,np.max(counts),color="red")
        ax_hist.set_xlim(0,max_)
        fig_hist.savefig(f"{parameters['analysis_path']}histograms_{file.split('.')[0]}.png")
        plt.close(fig_hist)
        
        #Crop
    b = parameters["cropping_cube"]
    image_preprocessed = image_preprocessed[b[0][0]:b[0][1], b[1][0]:b[1][1], b[2][0]:b[2][1]]

    return image_preprocessed

# Main functions
def execute(parameters):

    #List files to analyze
    files_list = [parameters["file_name"].format(t=i) for i in range(parameters["first"],parameters["last"]+1) if i not in parameters["not_to_do"]]
    numbers = [i for i in range(parameters["first"],parameters["last"]+1) if i not in parameters["not_to_do"]]

    #Check exist
    files_not_in = [i for i in files_list if i not in os.listdir(parameters["path_to_data"])]
    if len(files_not_in)>0:
        raise Exception(f"Some files do not exist in path_to_data \'{parameters['path_to_data']}\': {files_not_in}.")

    if os.path.exists(parameters["projection_path"]) and args.clean:
        shutil.rmtree(parameters["projection_path"])
        os.mkdir(parameters["projection_path"])
    elif not os.path.exists(parameters["projection_path"]):
        os.mkdir(parameters["projection_path"])

    folder = parameters["output_format"][:parameters["output_format"].rfind("/")]
    if os.path.exists(folder) and args.clean:
        shutil.rmtree(folder)
        os.mkdir(folder)
    elif not os.path.exists(folder):
        os.mkdir(folder)

    with Bar('Preprocessing sample files...', max = len(files_list)) as bar:

        for i,file in zip(numbers,files_list):
            #load images and downsample if indicated
            image = sitk.ReadImage(f"{parameters['path_to_data']}{file}")
            image.SetSpacing(parameters["voxel_size"])

            image_preprocessed = preprocessing(image,file,parameters)

            writer = sitk.ImageFileWriter()
            form = file.split('.')[-1]
            file = parameters["output_format"].format(t=i)
            writer.SetFileName(file)
            writer.Execute(image_preprocessed)

            #create projections (the plot code could be optimized)
            image_array_preprocessed = sitk.GetArrayFromImage(image_preprocessed)
            ims = [k for k,l in zip(parameters["voxel_size"],np.flip(image_array_preprocessed.shape))]

            fig_img, ax_img = plt.subplots(3,figsize=(10,30))
            max_ = np.percentile(image_array_preprocessed,parameters["saturation_percentile"])
            ax_img[0].imshow(image_array_preprocessed.max(axis=0),aspect=ims[1]/ims[0],vmax=max_)
            ax_img[0].set_xlabel("x"); ax_img[0].set_ylabel("y")
            ax_img[1].imshow(image_array_preprocessed.max(axis=1),aspect=ims[2]/ims[0],vmax=max_)
            ax_img[1].set_xlabel("x"); ax_img[1].set_ylabel("z")
            ax_img[2].imshow(image_array_preprocessed.max(axis=2),aspect=ims[2]/ims[1],vmax=max_)
            ax_img[2].set_xlabel("y"); ax_img[2].set_ylabel("z")
            fig_img.savefig(f"{parameters['projection_path']}{file.split('/')[-1].split('.')[0]}.png")
            plt.close(fig_img)

            bar.next()

def analysis(parameters):
    #List files to analyze
    files_list = [parameters["file_name"].format(t=i) for i in parameters["analysis_samples"] if i not in parameters["not_to_do"]]
    
    #Check exist
    files_not_in = [i for i in files_list if i not in os.listdir(parameters["path_to_data"])]
    if len(files_not_in)>0:
        raise Exception(f"Some files do not exist in path_to_data \'{parameters['path_to_data']}\': {files_not_in}.")
    
    if os.path.exists(parameters["analysis_path"]) and args.clean:
        shutil.rmtree(parameters["analysis_path"])
        os.mkdir(parameters["analysis_path"])
    elif not os.path.exists(parameters["analysis_path"]):
        os.mkdir(parameters["analysis_path"])

    with Bar('Preprocessing files...', max = len(files_list)) as bar:

        for i,file in enumerate(files_list):
            #load images and downsample if indicated
            image = sitk.ReadImage(f"{parameters['path_to_data']}{file}")

            image.SetSpacing(parameters["voxel_size"])

            image_preprocessed = preprocessing(image,file,parameters)

            image_array = sitk.GetArrayFromImage(image)
            image_array_preprocessed = sitk.GetArrayFromImage(image_preprocessed)

            #create projections (the plot code could be optimized)
            ims = [k for k,l in zip(parameters["voxel_size"],np.flip(image_array.shape))]
            imsp = [k for k,l in zip(parameters["voxel_size"],np.flip(image_array_preprocessed.shape))]

            fig_img, ax_img = plt.subplots(3,2,figsize=(20,30))

            max_ = np.percentile(image_array,parameters["saturation_percentile"])

            ax_img[0,0].imshow(image_array.max(axis=0),aspect=ims[1]/ims[0],vmax=max_)
            ax_img[0,0].set_xlabel("x"); ax_img[0,0].set_ylabel("y")
            ax_img[0,1].imshow(image_array_preprocessed.max(axis=0),aspect=ims[1]/ims[0],vmax=max_)
            ax_img[0,1].set_xlabel("x"); ax_img[0,1].set_ylabel("y")

            ax_img[1,0].imshow(image_array.max(axis=1),aspect=ims[2]/ims[0],vmax=max_)
            ax_img[1,0].set_xlabel("x"); ax_img[1,0].set_ylabel("z")
            ax_img[1,1].imshow(image_array_preprocessed.max(axis=1),aspect=ims[2]/ims[0],vmax=max_)
            ax_img[1,1].set_xlabel("x"); ax_img[1,1].set_ylabel("z")

            ax_img[2,0].imshow(image_array.max(axis=2),aspect=ims[2]/ims[1],vmax=max_)
            ax_img[2,0].set_xlabel("y"); ax_img[2,0].set_ylabel("z")
            ax_img[2,1].imshow(image_array_preprocessed.max(axis=2),aspect=ims[2]/ims[1],vmax=max_)
            ax_img[2,1].set_xlabel("y"); ax_img[2,1].set_ylabel("z")

            fig_img.savefig(f"{parameters['analysis_path']}projections_{file.split('.')[0]}.png")
            plt.close(fig_img)

            bar.next()

# Script
if args.analysis:
    analysis(parameters)
elif args.execute:
    execute(parameters)
else:
    raise Exception("You have to provide at least a flag (-a (analysis) or -x (execute)).")