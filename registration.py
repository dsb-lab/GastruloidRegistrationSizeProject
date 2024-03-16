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
from registrationtools import TimeRegistration
import time

#Parser
parser = argparse.ArgumentParser(
                    prog='Rigid registration',
                    description='This script goes over the rigid registration of the dataset.')

parser.add_argument('-r','--rigid',action='store_true',help="To execute rigid registation.")
parser.add_argument('-nl','--nonlinear',action='store_true',help="To execute non-linear registration.")
parser.add_argument('parameters',help="Parameters file of the experiment.")
args = parser.parse_args()

#Parameters
with open(args.parameters,"r") as file:
    parameters_ = json.load(file)
    parameters = {}
    for i,j in parameters_["image_info"].items():
        parameters[i] = j
    if args.rigid:
        for i,j in parameters_["rigid"].items():
            parameters[i] = j
    elif args.nonlinear:
        for i,j in parameters_["nonlinear"].items():
            parameters[i] = j

#Make unique json for executing rigid
file_name = "_tmp_parameters.json"
count = 1
while os.path.exists(file_name):
    file_name = "_tmp_parameters_{t:02d}.json".format(t=count)
json_object = json.dumps(parameters, indent=4)

with open(file_name, "w") as outfile:
    outfile.write(json_object)

# Functions
def registration(file):
    
    tr = TimeRegistration(file)
    tr.run_trsf()

    return

# Script
if args.rigid and args.nonlinear:
    raise Exception("Both flags -r and -nl cannot be used at the same time.")
elif not args.rigid and not args.nonlinear:
    raise Exception("Registration has to be executed with flag -r or -nl.")

try:
    registration(file_name)
    os.remove(file_name)
except:
    os.remove(file_name)
    raise Exception("Some error has occurred during registration.")