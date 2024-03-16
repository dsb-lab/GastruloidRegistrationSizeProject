# GastruloidRegistrationSizeProject
Pipeline to analyse time-lapse images and perform non-linear registration.

This project relies heavily on the [registration-tools](https://github.com/GuignardLab/registration-tools) from Guignard lab. The project adapts the package to perform a preprocessing of the data previous to the registration pipeline and to automatize the creation of a parameters folder for the project.

# Setting up the evironment

Clone the github project:

```
git clone https://github.com/dsb-lab/GastruloidRegistrationSizeProject
```

To setup the environment, you can create a conda environment directly from the `environment.yml`.

```
conda env create --name registrationenv --file=environment.yml
```

And whenever you want to perform a registration, activate the environment.

```
conda activate registrationenv
```

# Usage

The usage works around three scripts:

 - `setup.py`: To prepare for the analysis of a new dataset.
 - `preprocessing.py`: To preprocess the data before registration.
 - `registration.py`: To process rigid and lonlinear registration.

## setup.py

This script creates a new folder with everything prepared to analize a dataset.

To execute just write

```
python setup.py DIRECTORY FLAGS
```

The dataset folder should contain the images for the analysis.
The flags that can be added to the script are:

 - `-o` or `--output`: Name of the folder to create in which all the analysis results will be added. If not output is provided, a folder named `DIRECTORY_output` will be created.
 - `-f` or `--force`: If the folder exists, this will force to erase it and create anew folder from scratch.

After running this script, a folder with the following structure will be generated:

```
DIRECTORY_output
    files.csv : File containing the metainformation of all the files form the directory.
    parameters.json: A file containing all the parameters for the analysis steps.
```

The `parameters.json` would look like this:

```json
{
    "image_info": {
        "voxel_size": [
            0.2645833333333333,
            0.26458333333333334,
            2.5
        ],
        "first": 1,
        "last": 247,
        "not_to_do": []
    },
    "preprocessing": {
        "path_to_data": "DIRETORY/",
        "file_name": "XXXX_{t:03d}.tif",
        "analysis_path": "DIRECTORY_output/preprocessing-analysis/",
        "projection_path": "DIRECTORY_output/preprocessing-projections/",
        "output_format": "DIRECTORY_output/preprocessing-files/preprocessed_{t:03d}.tif",
        "analysis_samples": [1,247],
        "cropping_cube": [
            [
                0,
                2500
            ],
            [
                0,
                2500
            ],
            [
                0,
                200
            ]
        ],
        "saturation_percentile":99.999,
        "n_hist_bins": 100,
        "threshold": 0
    },
    "rigid": {
        "path_to_data": "DIRECTORY_output/preprocessing-files/",
        "file_name": "preprocessed_{t:03d}.tif",
        "trsf_folder": "DIRECTORY_output/rigid-transformations/",
        "output_format": "DIRECTORY_output/rigid-files/rigid_{t:03d}.tif",
        "projection_path": "DIRECTORY_output/rigid-projections/",
        "check_TP": 0,
        "compute_trsf": 1,
        "ref_TP": 1,
        "trsf_type": "rigid",
        "padding": 1,
        "recompute": 1,
        "apply_trsf": 1
    },
    "nonlinear": {
        "path_to_data": "DIRECTORY_output/rigid-files/",
        "file_name": "rigid_{t:03d}.tif",
        "trsf_folder": "DIRECTORY_output/nonlinear-transformations/",
        "output_format": "DIRECTORY_output/nonlinear-files/nonlinear_{t:03d}.tif",
        "projection_path": "DIRECTORY_output/nonlinear-projections/",
        "check_TP": 0,
        "compute_trsf": 1,
        "ref_TP": 1,
        "trsf_type": "vectorfield",
        "padding": 1,
        "recompute": 1,
        "apply_trsf": 1
    }
}
```

These parameters define the whole pipeline of work. The four keys correspond to:

 1. `image_info`: Shared parameters that will be used by all the information for all steps of the algorithm. These parameters will be added to the other key dictionaries before running the respective steps. The parameters in here can be overwritten by declaring them again the following keys. You can add any parameters from the [registration-tools manual](https://github.com/GuignardLab/registration-tools/blob/master/User-manual/usage/user-manual.pdf).
 2. `preprocessing`: Parameters that will be used during the preprocessing step. The parameters here will be defined in the next section.
 3. `rigid`: Parameters that will be used during the rigid registration step. You can add any parameters from the [registration-tools manual](https://github.com/GuignardLab/registration-tools/blob/master/User-manual/usage/user-manual.pdf).
 4. `nonlinear`: Parameters that will be used during the nonlinear registration step. You can add any parameters from the [registration-tools manual](https://github.com/GuignardLab/registration-tools/blob/master/User-manual/usage/user-manual.pdf).

This file is created already to have to be changed minimally for the registration tasks of this project, so in principle you should not need to add any more parameters than the ones present in it.

### Image_info parameters

The only parameters that you should check and modify if necessary after the setup are:

 - `image_info`/`voxel_size`: Make sure this numbers are proportional to the imaging resolution in XYZ.
 - `image_info`/`first`: The number in which the image sequences start. (e.g. `file_01.fit`, `file_02.fit`..., the number will be 1).
 - `image_info`/`last`: The final number of the sequence to be analysed.
 - `image_info`/`not_to_do`: The numbers that you want to skip from the analysis (e.g. corruption of the image).

## preprocessing.py

This step preprocess the raw files and prepares them for the posterior registration. In this project the preprocessing consists on two steps:

 1. Thresholding. All the pixels below certain threshold are set to zero.
 2. Cropping. We crop the image to only focus the volume of interest. This saves memory and computation time in the following registration step.

### Preprocessing parameters

 - `path_to_data`: Folder where the raw data is contained.
 - `file_name`: This should contain the pattern of the name of the images. (e.g. if you images llok like `t0001.tif`, the pattern should be `t{t:04d}.tif`; if they are like `t_01_488.tif`, in which is the second number the one changing, then `t_{t:02d}_488.tif`).
 - `analysis_path`: Folder where the analysis plots will be stored.
 - `projection_path`: Folder where the maximum intensity projections will be stored.
 - `output_format`: Folder and naming of the output preprocessed files. **This has been automatically generated to be consistent with the rigid parameters. If you change the name, you will have to change it correspondingly in the rigid section.**
 - `analysis_samples`: Liat of samples to use for the analysis step of the preprocessing.
 - `cropping_cube`: List stating the XYZ limits to crop the data.
 - `saturation_percentile`: Percentile to use for saturating the projection image plots.
 - `n_hist_bins`: Number of bins to use to generate the histogram plots for thresholding.
 - `threshold`: Threshold value used for the thresholding step. If 0, no thresholding will happen.


### Preprocessing steps

Since the data files are usually large, preprocessing can be a slow task so, it is not suitable to tune the preprocessing parameters by "try-and-error" over all the data points. Instead, run the process with the `--analysis` (or `-a`) flag to just run the preprocessing over the selected files defined in `analysis_samples` and use the generated plots to set the preprocessing parameters.

```
python preprocessing.py DIRECTORY_output/parameters.json -a
```

After you are happy with the results, execute the preprocessing over all the data points using the `--execute` (or `-x`) command.

```
python preprocessing.py DIRECTORY_output/parameters.json -x
```
and all the files will be processed.

### Customizing the preprocessing (For developers)

If you find that a different preprocessing pipeline would be necessary for your data you will have to change two things (at least for small modifications of the pipeline):

 1. In `preprocessing.py`: Modity the function `preprocessing`.
 2. Add any additional parameters that the pipeline uses inside `setup.py` in function `create_parameters_json`, wich creates the base json file.

## registration.py

The registration is produced in two steps:

 1. Rigid registration to compensate for the global movement of the image.
 2. Nonlinear registration to extract the movement flux.

The parameters file already incorporats the parameters used for both steps and shouldn't be necessary to modify it. But in case more parameters would be required, any from [registration-tools manual](https://github.com/GuignardLab/registration-tools/blob/master/User-manual/usage/user-manual.pdf) could be incorporated.

### Registration steps

First execute the rigid registration to compensate global shifts with the `--rigid` (or `-r`) flag:

```
python registration.py DIRECTORY_output/parameters.json -r
```

Once corrected, you can run the nonlinear using the `--nonlinear` (or `-nl`) flag:

```
python registration.py DIRECTORY_output/parameters.json -nl
```
